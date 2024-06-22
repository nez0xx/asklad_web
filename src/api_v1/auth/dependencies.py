from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.api_v1.auth.crud import get_user_by_email
from src.api_v1.auth.service import get_current_token_payload, TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE
from src.core.database import User, db_helper


async def get_current_user(
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        payload=Depends(get_current_token_payload)
):

    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password",
    )

    if payload[TOKEN_TYPE_FIELD] != ACCESS_TOKEN_TYPE:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type: access expected"
        )

    user_email = payload["email"]
    user = await get_user_by_email(session, user_email)

    if user:
        return user
    raise unauthed_exc


def check_user_is_verify(user: User = Depends(get_current_user)):
    if not user.is_verify:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Verify your account")
