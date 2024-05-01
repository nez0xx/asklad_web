import secrets
import uuid
from typing import Any, Annotated
from fastapi import APIRouter, HTTPException, Depends, status, Header, Response, Cookie
from fastapi.security import HTTPBasicCredentials, HTTPBasic, HTTPBearer
from . import utils, jwt_auth
from auth.jwt_auth import validate_auth_user, get_current_user, get_jwt_token_payload, create_access_token, \
    get_current_user_for_refresh
from auth.schemas import UserSchema, TokenInfo


http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/auth", dependencies=[Depends(http_bearer)])

security = HTTPBasic()



DB_COOKIES: dict[str, dict[str, Any]] = {}
COOKIE_SESSION_ID = "web-app-session-id"

def generate_session_id() -> str:
    return uuid.uuid4().hex
'''
def get_username_header(token = Header(alias="x-auth-token")):
    username = data.get(token)
    if username:
        return username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid",
    )

def get_session_data(
    session_id: str = Cookie(alias=COOKIE_SESSION_ID),
) -> dict:
    if session_id not in DB_COOKIES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated",
        )

    return DB_COOKIES[session_id]

'''

@router.post("/login", response_model=TokenInfo)
def auth_user_issue_jwt(
    user: UserSchema = Depends(validate_auth_user),
):
    access_token = jwt_auth.create_access_token(user)
    refresh_token = jwt_auth.create_refresh_token(user)

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.get('/users/me', response_model=UserSchema)
def get_me(user: UserSchema = Depends(get_current_user)):

    return user


@router.get("/refresh", )
def refresh_token(user: UserSchema = Depends(get_current_user_for_refresh)):
    access_token = create_access_token(user)
    return TokenInfo(
        access_token=access_token
    )







'''
@router.get("/check-cookie/")
def demo_auth_check_cookie(
    user_session_data: dict = Depends(get_session_data),
):
    username = user_session_data["username"]
    return {
        "message": f"Hello, {username}!",
        **user_session_data,
    }
'''