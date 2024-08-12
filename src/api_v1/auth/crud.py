import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.api_v1.auth.schemas import RegisterUser
from src.api_v1.auth.security import hash_password
from src.core.database import User, EmailConfirmToken
from src.core.database.db_model_reset_token import ResetToken

from datetime import datetime, timezone, timedelta


async def create_user(session: AsyncSession, user_schema: RegisterUser):

    hashed_password = user_schema.hashed_password
    email = user_schema.email

    user = User(
        hashed_password=hashed_password,
        email=email,
        name=user_schema.name,
        is_verify=False
    )

    session.add(user)

    await session.commit()
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:

    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:

    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def create_email_confirm_token(session: AsyncSession, user_id: int) -> str:
    token = uuid.uuid4().hex
    now = datetime.now()
    token_model = EmailConfirmToken(token=token, user_id=user_id, created_at=now)
    session.add(token_model)
    await session.commit()
    await session.close()
    return token


async def get_email_confirm_token(session: AsyncSession, token: str) -> EmailConfirmToken | None:
    stmt = (select(EmailConfirmToken)
            .options(joinedload(EmailConfirmToken.user_relationship))
            .where(EmailConfirmToken.token == token))
    result = await session.execute(stmt)
    token_model = result.scalar_one_or_none()
    return token_model


async def delete_email_confirm_token(session: AsyncSession, token: str):
    stmt = (delete(EmailConfirmToken)
            .where(EmailConfirmToken.token == token))
    await session.execute(stmt)
    await session.commit()


async def create_reset_token(session: AsyncSession, user_id: int) -> str:
    token = uuid.uuid4().hex
    expired_at = datetime.now() + timedelta(minutes=10)
    token_model = ResetToken(token=token, user_id=user_id, expired_at=expired_at)
    session.add(token_model)
    await session.commit()
    await session.close()
    return token


async def get_reset_token(session: AsyncSession, token: str) -> ResetToken | None:
    now = datetime.now()
    stmt = (select(ResetToken)
            .where(ResetToken.token == token)
            .where(ResetToken.expired_at > now))
    result = await session.execute(stmt)
    token_model = result.scalar_one_or_none()
    return token_model


async def get_active_reset_token_by_user_id(session: AsyncSession, user_id: int) -> ResetToken | None:
    now = datetime.now()
    stmt = (select(ResetToken)
            .where(ResetToken.user_id == user_id)
            .where(ResetToken.expired_at > now))
    result = await session.execute(stmt)
    token_model = result.scalar_one_or_none()
    return token_model


async def delete_reset_token(session: AsyncSession, token: str):
    stmt = delete(ResetToken).where(ResetToken.token == token)
    await session.execute(stmt)
    await session.commit()


async def set_password(session: AsyncSession, user_id: int, password: str):
    user = await get_user_by_id(session=session, user_id=user_id)
    user.hashed_password = hash_password(password).decode()
    await session.commit()



