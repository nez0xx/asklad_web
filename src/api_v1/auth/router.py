from fastapi.security import HTTPBasic, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import db_helper, User
from fastapi import APIRouter, Depends, Response, Request
from . import service


from src.api_v1.auth.service import (
    create_access_token,
    get_current_user_for_refresh, reset_password_request
)
from .dependencies import get_current_user

from src.api_v1.auth.schemas import (
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
    user_schema: RegisterUser,
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    await service.register_user(session, user_schema)


@router.post("/login", response_model=TokenInfo)
async def auth_user_issue_jwt(
    user_data: AuthUser,
    response: Response,
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),

):
    user = await service.authenticate_user(user_data, session)

    access_token = service.create_access_token(user.email)
    refresh_token = service.create_refresh_token(user.email)

    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)

    return TokenInfo(
        access_token=access_token
    )


@router.get('/me')
async def get_me(user: User = Depends(get_current_user)):

    return user


@router.post('/change_password')
async def change_password(
        password: str,
        new_password: str,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    await service.change_password(
        session=session,
        password=password,
        new_password=new_password,
        user=user
    )


@router.get("/refresh")
def refresh(
        user: User = Depends(get_current_user_for_refresh)
):
    access_token = create_access_token(user.email)

    return TokenInfo(
        access_token=access_token
    )


@router.post("/confirm/")
async def confirm_email_view(
    token: str,
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    await service.confirm_email(session, token)


@router.get("/reset_pass/{token}")
async def check_password_reset_token_exists(
        token: str,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    return await service.reset_token_exists(session=session, token=token)


@router.post("/reset_pass/request")
async def create_reset_password_request(
        user_email: str,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    await reset_password_request(session=session, user_email=user_email)


@router.post("/reset_pass/")
async def reset_password_view(
        token: str,
        password: str,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    await service.reset_password(session=session, token=token, new_password=password)




