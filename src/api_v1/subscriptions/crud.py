from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Subscription, Tariff


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
            (Subscription.expired_at > datetime.now(tz=timezone(offset=timedelta(hours=5)))) &
            (Subscription.started_at < datetime.now(tz=timezone(offset=timedelta(hours=5))))
        )
    )
    print(datetime.now(tz=timezone(offset=timedelta(hours=5))))
    result = await session.execute(stmt)
    print(result, result.all())
    return await session.scalar(statement=stmt)


async def create_subscription_in_db(
        session: AsyncSession,
        expired_at: datetime,
        user_id: int,
        # price: int,
        tariff_id: int,
        started_at: datetime | None = None
) -> Subscription:
    now = datetime.now(tz=None) + timedelta(hours=3)

    new_sub = Subscription(
        user_id=user_id,
        expired_at=expired_at,
        created_at=now,
        tariff_id=tariff_id
    )
    if started_at:
        new_sub.started_at = started_at

    session.add(new_sub)
    await session.commit()

    return new_sub


async def get_tariff_by_id(session: AsyncSession, tariff_id: int):
    stmt = select(Tariff).where(Tariff.id == tariff_id)
    result = await session.execute(stmt)
    tariff = result.scalar_one_or_none()
    return tariff


async def get_all_tariffs(session: AsyncSession):
    stmt = select(Tariff)
    result = await session.execute(stmt)
    tariffs = result.scalars().all()
    return tariffs
