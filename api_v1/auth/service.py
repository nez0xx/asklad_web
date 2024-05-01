from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.auth.exceptions import InvalidCredentials

from api_v1.auth import crud
from api_v1.auth.schemas import AuthUser
from api_v1.auth.security import check_password
from core.database import User



async def authenticate_user(
        user_schema: AuthUser,
        session: AsyncSession,
) -> User:

    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )

    user = await crud.get_user_by_email(
        email=user_schema.email,
        session=session
    )

    if not user:
        raise unauthed_exc

    if not check_password(
            plain_password=user_schema.hashed_password,
            hashed_password=user.hashed_password
    ):
        raise unauthed_exc

    return user