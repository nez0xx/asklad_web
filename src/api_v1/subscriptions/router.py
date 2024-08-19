import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.subscriptions import crud
from src.api_v1.subscriptions.dependencies import check_active_subscription_depends
from src.api_v1.subscriptions.service import create_subscription_service
from src.core.database import User, Subscription
from src.core.database.db_helper import db_helper
from fastapi.security import HTTPBearer
from src.api_v1.auth.dependencies import check_user_is_verify, get_current_user

http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
    dependencies=[Depends(http_bearer)]
)


@router.post(path="/create")
async def create_subscription(
        tariff_id: int,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):

    payment_link = await create_subscription_service(session=session, tariff_id=tariff_id, user_id=user.id)
    return payment_link


@router.get(path="/check")
async def check_sub(
    sub: Subscription = Depends(check_active_subscription_depends)
):
    pass


@router.get(path="/tariffs")
async def get_tariffs_list(session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)):
    tariffs = await crud.get_all_tariffs(session=session)
    return tariffs
