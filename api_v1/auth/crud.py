from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.schemas import RegisterUser
from core.database import User
from core.database.db_model_email_confirm_token import EmailConfirmToken


async def create_user(session: AsyncSession, user_schema: RegisterUser):

    hashed_password = user_schema.hashed_password
    email = user_schema.email

    user = User(hashed_password=hashed_password, email=email)

    session.add(user)

    await session.commit()
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:

    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user


async def create_or_override_confirm_token(session: AsyncSession, user: User):
    stmt = delete(EmailConfirmToken).where(EmailConfirmToken.user_id == user.id)
    await session.execute(stmt)

    token = EmailConfirmToken(user_id=user.id)
    session.add(token)
    await session.commit()

    return token


async def delete_token(session: AsyncSession, user_id: int):
    stmt = delete(EmailConfirmToken).where(EmailConfirmToken.user_id == user_id)
    await session.execute(stmt)
    await session.commit()
