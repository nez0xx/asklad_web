import uuid
from typing import Any
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasic, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import db_helper, User
from . import crud, service

from api_v1.auth.service import get_current_user, create_access_token, \
    get_current_user_for_refresh

from api_v1.auth.schemas import UserSchema, TokenInfo, RegisterUser, AuthUser

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/auth", dependencies=[Depends(http_bearer)])

security = HTTPBasic()

DB_COOKIES: dict[str, dict[str, Any]] = {}
COOKIE_SESSION_ID = "web-app-session-id"


@router.post("/signup")
async def register_user(
    user_info: RegisterUser,
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    user = await crud.create_user(session, user_info)
    return user


def generate_session_id() -> str:
    return uuid.uuid4().hex


@router.post("/login", response_model=TokenInfo)
async def auth_user_issue_jwt(
    user_data: AuthUser,
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):

    user = await service.authenticate_user(user_data, session)

    access_token = service.create_access_token(user.email)
    refresh_token = service.create_refresh_token(user.email)

    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token
    )



@router.get('/users/me')
def get_me(user: User = Depends(get_current_user)):
    return user



@router.get("/refresh")
def refresh_token(
        user: UserSchema = Depends(get_current_user_for_refresh)
):
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