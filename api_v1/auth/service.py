from datetime import timedelta
from email.mime.text import MIMEText

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.crud import get_user_by_email

from api_v1.auth import crud, utils
from api_v1.auth.schemas import AuthUser, RegisterUser
from api_v1.auth.security import check_password
from core.database import User, db_helper
from core.settings import settings
from smtp import send_message

TOKEN_TYPE_FIELD = "type"

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


http_bearer = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)


def get_current_token_payload(token=Depends(oauth2_scheme)):

    try:
        payload = utils.decode_jwt(token)

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
            # detail=f"invalid token error",
        )

    return payload


async def get_current_user(
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        payload=Depends(get_current_token_payload)
):

    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )

    if payload[TOKEN_TYPE_FIELD] != ACCESS_TOKEN_TYPE:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type: access expected"
        )

    user_email = payload["email"]
    user = await get_user_by_email(session, user_email)

    if user:
        return user
    raise unauthed_exc


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
    print(payload)
    token = utils.encode_jwt(payload, expire_minutes=expire_minutes)

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

    user = await crud.get_user_by_email(
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
    return f"127.0.0.1:8000/auth/confirm/{token}"


async def register_user(session: AsyncSession, user_schema: RegisterUser):
    user = await crud.get_user_by_email(
        session=session,
        email=user_schema.email
    )
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")
    user = await crud.create_user(session, user_schema=user_schema)

    confirm_token = utils.encode_jwt(payload={"email": user_schema.email})

    link = create_confirm_email_link(confirm_token)

    print(link)

    message = MIMEText(f'<a href="{link}">Verify</a>', 'html')
    send_message(user_schema.email, message=message.as_string())

    return user


async def confirm_email(session: AsyncSession, token: str):

    payload = utils.decode_jwt(token)

    user = await crud.get_user_by_email(
        session=session,
        email=payload["email"]
    )
    user.is_verify = True

    await session.commit()

    await crud.delete_token(
        session=session,
        user_id=user.id
    )

    return "success"
