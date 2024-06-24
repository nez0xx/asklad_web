from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.auth.schemas import RegisterUser
from src.api_v1.auth.security import hash_password
from src.api_v1.auth.utils import generate_id
from src.core.database import User
from src.core.database.db_model_reset_token import ResetToken

from datetime import datetime, timezone, timedelta


async def create_user(session: AsyncSession, user_schema: RegisterUser):

    hashed_password = user_schema.hashed_password
    email = user_schema.email

    user = User(hashed_password=hashed_password, email=email, is_verify=True)

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


async def create_reset_token(session: AsyncSession, user_id: int) -> str:
    token = generate_id()
    expired_at = datetime.now(tz=timezone(offset=timedelta(hours=5))) + timedelta(hours=1)
    token_model = ResetToken(token=token, user_id=user_id, expired_at=expired_at)
    session.add(token_model)
    await session.commit()
    await session.close()
    return token


async def get_reset_token(session: AsyncSession, token: str) -> ResetToken | None:
    now = datetime.now(tz=timezone(offset=timedelta(hours=5)))
    stmt = (select(ResetToken)
            .where(ResetToken.token == token)
            .where(ResetToken.expired_at > now))
    result = await session.execute(stmt)
    token_model = result.scalar_one_or_none()
    return token_model


async def deactivcate_token(session: AsyncSession, token: str):
    token_model = await get_reset_token(session=session, token=token)
    now = datetime.now(tz=timezone(offset=timedelta(hours=5)))
    token_model.expired_at = now
    await session.commit()


async def set_password(session: AsyncSession, user_id: int, password: str):
    user = await get_user_by_id(session=session, user_id=user_id)
    user.hashed_password = hash_password(password).decode()
    await session.commit()



