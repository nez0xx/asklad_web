import uuid
from datetime import timedelta

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.auth.constants import TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from src.api_v1.auth.crud import create_email_confirm_token
from src.api_v1.utils import encode_jwt, decode_jwt
from src.core import settings
from src.smtp import send_email

from fastapi import status

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)


def get_current_token_payload(token=Depends(oauth2_scheme)):

    try:
        payload = decode_jwt(token)

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
            # detail=f"invalid token error",
        )

    return payload


def create_jwt(
        token_type: str,
        payload: dict,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None
) -> str:

    payload[TOKEN_TYPE_FIELD] = token_type

    token = encode_jwt(payload, expire_minutes=expire_minutes)

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
    refresh_token = create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        payload=payload,
        expire_minutes=settings.auth_jwt.refresh_token_expire_minutes
    )
    return refresh_token


def generate_id() -> str:
    return uuid.uuid4().hex


def create_confirm_email_link(token: str):
    return f"{settings.HOST}/#/confirm_email/{token}"


async def send_confirm_link(session: AsyncSession, email: str, user_id):
    confirm_token = await create_email_confirm_token(session=session, user_id=user_id)

    link = create_confirm_email_link(confirm_token)
    html = u'''
        <html>
            <head></head>
            <body>
            <p>Verify your account --></p>
                <a href="%s">Verify</a>
                %s
            </body>
        </html>
        ''' % (link, link)

    send_email(email, html_message=html, subject="Регистрация")
