from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.subscriptions.crud import get_tariff_by_id, create_subscription_in_db, \
    get_active_subscription_by_user_id
from src.api_v1.subscriptions.payment_system.service import create_payment


async def create_subscription_service(session: AsyncSession, tariff_id: int, user_id: int):

    existing_subscription = await get_active_subscription_by_user_id(session=session, user_id=user_id)
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subscription already exists"
        )

    tariff = await get_tariff_by_id(session=session, tariff_id=tariff_id)
    expired_at = datetime.now(tz=None) + timedelta(days=tariff.expire_days)

    subscription = await create_subscription_in_db(
        session=session,
        expired_at=expired_at,
        user_id=user_id,
        tariff_id=tariff_id
    )

    payment_link = await create_payment(
        session=session,
        value=tariff.price_rub,
        user_id=user_id,
        currency="RUB",
        subscription_id=subscription.id
    )

    return payment_link
