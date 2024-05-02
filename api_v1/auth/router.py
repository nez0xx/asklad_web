from fastapi.security import HTTPBasic, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import db_helper, User
from fastapi import APIRouter, Depends
from . import crud, service
from typing import Any

from api_v1.auth.service import (
    get_current_user,
    create_access_token,
    get_current_user_for_refresh
)

from api_v1.auth.schemas import (
    UserSchema,
    TokenInfo,
    RegisterUser,
    AuthUser
)


http_bearer = HTTPBearer(auto_error=False)
security = HTTPBasic()


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    dependencies=[Depends(http_bearer)]
)


@router.post("/signup")
async def register_user(
    user_info: RegisterUser,
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    user = await crud.create_user(session, user_info)
    return user


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

@router.get('/me')
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

