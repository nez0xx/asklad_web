from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.subscriptions.crud import get_tariff_by_id, create_subscription_in_db


async def create_subscription_service(session: AsyncSession, tariff_id: int, user_id: int):

    tariff = await get_tariff_by_id(session=session, tariff_id=tariff_id)
    expired_at = datetime.now() + timedelta(days=tariff.expire_days)
    sub = await create_subscription_in_db(
        session=session,
        expired_at=expired_at,
        user_id=user_id
    )

    return sub
