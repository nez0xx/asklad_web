from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Subscription


async def get_active_subscription_by_user_id(
        user_id: int,
        session: AsyncSession,
) -> Subscription | None:
    stmt = (
        select(
            Subscription
        )
        .where(
            (Subscription.user_id == user_id) &
            (Subscription.is_active == True) &
            (Subscription.expired_at > datetime.now(tz=timezone.utc)) &
            (Subscription.started_at < datetime.now(tz=timezone.utc))
        )
    )

    return await session.scalar(statement=stmt)


async def create_subscription_in_db(
        session: AsyncSession,
        expired_at: datetime,
        user_id: int,
        # price: int,
        # tariff_id: str,
        started_at: datetime | None = None
):
    new_sub = Subscription(
        user_id=user_id,
        expired_at=expired_at
    )
    if started_at:
        new_sub.started_at = started_at

    session.add(new_sub)
    await session.commit()

    return new_sub
