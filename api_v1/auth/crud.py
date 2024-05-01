from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import User


async def get_user_by_email(session: AsyncSession, email) -> User | None:

    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    return user
