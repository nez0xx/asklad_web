from datetime import timedelta

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

import src.api_v1.utils
from src.api_v1.auth.crud import get_user_by_email, create_reset_token, create_user, set_password, get_reset_token, \
    get_user_by_id, deactivcate_token

from src.api_v1.auth import crud, utils
from src.api_v1.auth.schemas import AuthUser, RegisterUser
from src.api_v1.auth.security import check_password, hash_password
from src.api_v1.auth.utils import generate_id
from src.core.database import User, db_helper
from src.core.settings import settings
from src.smtp import send_email

TOKEN_TYPE_FIELD = "type"

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


http_bearer = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)


def get_current_token_payload(token=Depends(oauth2_scheme)):

    try:
        payload = src.api_v1.utils.decode_jwt(token)

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
            # detail=f"invalid token error",
        )

    return payload


async def get_current_user_for_refresh(
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        payload=Depends(get_current_token_payload)
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    if payload[TOKEN_TYPE_FIELD] != REFRESH_TOKEN_TYPE:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type: refresh expected"
        )

    user = await get_user_by_email(
        session=session,
        email=payload["sub"]
    )

    if user:
        return user

    raise unauthed_exc


def create_jwt(
        token_type: str,
        payload: dict,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None
) -> str:

    payload[TOKEN_TYPE_FIELD] = token_type

    token = src.api_v1.utils.encode_jwt(payload, expire_minutes=expire_minutes)

    return token


def create_access_token(user_email):
    payload = {
        "sub": user_email,
        "email": user_email
    }
    access_token = create_jwt(ACCESS_TOKEN_TYPE, payload)
    return access_token


def create_refresh_token(user_email):
    payload = {
        "sub": user_email
    }
    refresh_token = create_jwt(REFRESH_TOKEN_TYPE, payload, expire_minutes=10)
    return refresh_token


async def authenticate_user(
        user_schema: AuthUser,
        session: AsyncSession,
) -> User:

    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )

    user = await get_user_by_email(
        email=user_schema.email,
        session=session
    )

    if not user:
        raise unauthed_exc

    if not check_password(
            password=user_schema.password,
            hashed_password=user.hashed_password
    ):
        raise unauthed_exc

    return user


def create_confirm_email_link(token: str):
    return f"{settings.HOST}/auth/confirm/{token}"


async def register_user(session: AsyncSession, user_schema: RegisterUser):
    user = await get_user_by_email(
        session=session,
        email=user_schema.email
    )
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")
    user = await create_user(session, user_schema=user_schema)

    confirm_token = src.api_v1.utils.encode_jwt(payload={"email": user_schema.email}, expire_minutes=24*60)

    link = create_confirm_email_link(confirm_token)
    print(link)
    html = u'''\
    <html>
        <head></head>
        <body>
        <p>Verify your account --></p>
            <a href="%s">Verify</a>
        </body>
    </html>
    ''' % link

    #send_message(user_schema.email, html_message=html)

    return user


async def confirm_email(session: AsyncSession, token: str):

    payload = src.api_v1.utils.decode_jwt(token)

    user = await get_user_by_email(
        session=session,
        email=payload["email"]
    )
    user.is_verify = True

    await session.commit()

    return "success"


async def change_password(
        session: AsyncSession,
        password: str,
        new_password: str,
        user: User
):
    if not check_password(password=password, hashed_password=user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid password"
        )
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be longer than 8 characters"
        )
    await set_password(session=session, user_id=user.id, password=new_password)


async def reset_password_request(
        session: AsyncSession,
        user_email: str
):
    user = await get_user_by_email(session=session, email=user_email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")

    token = await create_reset_token(session=session, user_id=user.id)
    send_email(email_to=user_email, html_message="link/{token}")
    print(token)


async def reset_token_exists(session: AsyncSession, token: str):
    token_model = await get_reset_token(session=session, token=token)
    return token_model != None


async def reset_password(session: AsyncSession, token: str, new_password: str):
    token_model = await get_reset_token(session=session, token=token)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token does not exist"
        )

    user = await get_user_by_id(session=session, user_id=token_model.user_id)

    await set_password(session=session, user_id=user.id, password=new_password)
    await deactivcate_token(session=session, token=token)


