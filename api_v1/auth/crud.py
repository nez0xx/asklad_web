from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.schemas import RegisterUser
from core.database import User


async def create_user(session: AsyncSession, user_info: RegisterUser):

    hashed_password = user_info.hashed_password
    email = user_info.email

    user = User(hashed_password=hashed_password, email=email)

    session.add(user)

    await session.commit()
    return user


async def get_user_by_email(session: AsyncSession, email) -> User | None:

    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    print(user, '-'*100)
    return user
