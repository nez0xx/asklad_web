from datetime import timedelta

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.crud import get_user_by_email

from api_v1.auth import crud, utils
from api_v1.auth.schemas import AuthUser
from api_v1.auth.security import check_password
from core.database import User, db_helper
from core.settings import settings

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


def get_current_user_for_refresh(
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

    user = get_user_by_email(session)
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
    token = utils.encode_jwt(payload)

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
    refresh_token = create_jwt(REFRESH_TOKEN_TYPE, payload)
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
