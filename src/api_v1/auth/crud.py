from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.auth.schemas import RegisterUser
from src.core.database import User


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

