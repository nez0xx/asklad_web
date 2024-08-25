from datetime import timedelta

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

from jwt import InvalidTokenError, ExpiredSignatureError

from sqlalchemy.ext.asyncio import AsyncSession

from .constants import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    TOKEN_TYPE_FIELD
)

from src.api_v1.auth.crud import (
    get_user_by_email,
    create_reset_token,
    create_user,
    set_password,
    get_reset_token,
    get_user_by_id,
    delete_reset_token,
    get_active_reset_token_by_user_id,
    get_email_confirm_token,
    delete_email_confirm_token
)

from src.api_v1.utils import get_email_template, decode_jwt

from src.api_v1.auth.schemas import AuthUser, RegisterUser
from src.api_v1.auth.security import check_password, hash_password
from src.api_v1.auth.utils import generate_id, create_jwt, send_confirm_link

from src.core.database import User, db_helper, ResetToken
from src.core.settings import settings

from src.exceptions import NotFound

from src.smtp import send_email


http_bearer = HTTPBearer()


async def get_current_user_for_refresh(
        request: Request,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token is None",
    )

    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        raise unauthed_exc

    try:
        payload = decode_jwt(refresh_token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature has expired",
        )

    user = await get_user_by_email(
        session=session,
        email=payload["sub"]
    )
    if user:
        return user
    raise unauthed_exc


async def authenticate_user(user_schema: AuthUser, session: AsyncSession) -> User:

    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неправильный логин или пароль",
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

    if user.is_verify is False:
        await send_confirm_link(session=session, email=user_schema.email, user_id=user.id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Подтвердите ваш аккаунт. Ссылка отправлена на ваш email."
        )

    return user


async def register_user(session: AsyncSession, user_schema: RegisterUser) -> User:
    user = await get_user_by_email(
        session=session,
        email=user_schema.email
    )
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует"
        )
    else:
        user = await create_user(session, user_schema=user_schema)
    await send_confirm_link(session=session, email=user_schema.email, user_id=user.id)
    return user


async def confirm_email(session: AsyncSession, token: str):

    token_model = await get_email_confirm_token(session=session, token=token)
    if token_model is None:
        raise NotFound()

    user = token_model.user_relationship
    user.is_verify = True
    await delete_email_confirm_token(session=session, token=token)
    await session.commit()


async def change_password(session: AsyncSession, password: str, new_password: str, user: User):
    if not check_password(password=password, hashed_password=user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неправильный пароль"
        )
    #if len(new_password) < 8:
        #raise HTTPException(
        #    status_code=status.HTTP_400_BAD_REQUEST,
        #    detail="Password must be longer than 8 characters"
        #)
    await set_password(session=session, user_id=user.id, password=new_password)


async def get_active_reset_token(session: AsyncSession, user_id: int) -> ResetToken | None:
    token_model = await get_active_reset_token_by_user_id(session=session, user_id=user_id)
    return token_model


async def reset_token_exists(session: AsyncSession, token: str):
    token_model = await get_reset_token(session=session, token=token)
    return token_model != None


async def reset_password_request(session: AsyncSession, user_email: str):
    user = await get_user_by_email(session=session, email=user_email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователя не существует")

    existing_token = await get_active_reset_token(session=session, user_id=user.id)

    if existing_token:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Запрос на сброс пароля уже сделан. Повторите попытку через 10 минут"
        )

    token = await create_reset_token(session=session, user_id=user.id)

    link = f"{settings.HOST}/#/reset_password/{token}"

    template = get_email_template()
    html = template.render(
        preheader="Подтвердите действие на сайте asklad.pro",
        title="А.Склад",
        logo_url="https://asklad.pro/assets/logo-vGv-sIDM.png",
        subject="Сброс пароля",
        header_text="Нажмите на кнопку, чтобы сбросить пароль от аккаунта А.Склад",
        button_link=link,
        button_text="Сбросить",
        alternative_link=link,
        footer_text="Если вы не регистрировались на сайте asklad.pro, проигнорируйте это сообщение",
        company_info="А.Склад"
    )

    send_email(email_to=user_email, html_message=html, subject="Сброс пароля")


async def reset_password(session: AsyncSession, token: str, new_password: str):
    token_model = await get_reset_token(session=session, token=token)
    if token_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token does not exist"
        )

    user = await get_user_by_id(session=session, user_id=token_model.user_id)

    await set_password(session=session, user_id=user.id, password=new_password)
    await delete_reset_token(session=session, token=token)


async def change_name_service(session: AsyncSession, new_name: str, user: User):
    if len(new_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Имя слишком короткое"
        )
    user.name = new_name
    await session.commit()
    await session.close()
