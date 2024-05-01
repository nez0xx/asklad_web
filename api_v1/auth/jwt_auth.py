from fastapi import HTTPException, Form, status, Depends
from jwt import InvalidTokenError

from .schemas import UserSchema
from . import security, utils
from fastapi.security import OAuth2PasswordBearer, HTTPBearer

from datetime import timedelta

from core.settings import setsecur

TOKEN_TYPE_FIELD = "type"

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


http_bearer = HTTPBearer()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)

ivan = UserSchema(
    username="Ivan",
    password=security.hash_password("parmezan777")
)

marianna = UserSchema(
    username="m1eonva",
    password=security.hash_password("911gt3rs")
)

users_db = {
    ivan.username: ivan,
    marianna.username: marianna
}


def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
        ):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    if not (user := users_db.get(username)):
        raise unauthed_exc

    if not (security.check_password(
        password=password,
        hashed_password=user.password,
    )):
        raise unauthed_exc

    return user


def get_jwt_token_payload(token=Depends(oauth2_scheme)):
    try:
        print(token)
        payload = utils.decode_jwt(token)
    except InvalidTokenError as e:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
            # detail=f"invalid token error",
        )
    return payload


def get_current_user(payload=Depends(get_jwt_token_payload)):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    print(payload)
    if user := users_db.get(payload['sub']):
        return user

    raise unauthed_exc


def get_current_user_for_refresh(payload=Depends(get_jwt_token_payload)):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )
    if payload[TOKEN_TYPE_FIELD] != REFRESH_TOKEN_TYPE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type: refresh expected"
        )

    if user := users_db.get(payload['sub']):
        return user

    raise unauthed_exc
def create_jwt(token_type: str,
               payload: dict,
               expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
               expire_timedelta: timedelta | None = None
               ) -> str:

    payload[TOKEN_TYPE_FIELD] = token_type
    token = utils.encode_jwt(payload)

    return token


def create_access_token(user: UserSchema):
    payload = {
        "sub": user.username,
        "username": user.username
    }
    access_token = create_jwt(ACCESS_TOKEN_TYPE, payload)
    return access_token


def create_refresh_token(user: UserSchema):
    payload = {
        "sub": user.username
    }
    refresh_token = create_jwt(REFRESH_TOKEN_TYPE, payload)
    return refresh_token


