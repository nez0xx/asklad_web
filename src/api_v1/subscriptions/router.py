import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.subscriptions import crud
from src.api_v1.subscriptions.dependencies import check_active_subscription_depends
from src.core.database import User, Subscription
from src.core.database.db_helper import db_helper
from fastapi.security import HTTPBearer
from src.api_v1.auth.dependencies import check_user_is_verify, get_current_user

http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
    dependencies=[Depends(http_bearer), Depends(check_user_is_verify)]
)


@router.post(path="/create")
async def create_subscription(
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):
    expired_at = datetime.now(tz=timezone(offset=timedelta(hours=5))) + timedelta(minutes=5)

    sub = await crud.create_subscription_in_db(
        session=session,
        expired_at=expired_at,
        user_id=user.id
    )

    return sub


@router.get(path="/check")
async def check_sub(
    sub: Subscription = Depends(check_active_subscription_depends)
):
    pass
