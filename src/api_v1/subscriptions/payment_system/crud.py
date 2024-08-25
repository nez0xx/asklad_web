from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Payment


async def create_payment_model(
        session: AsyncSession,
        order_id: str,
        order_price: int,
        currency: str,
        user_id: int,
        subscription_id: int
):
    payment = Payment(
        order_id=order_id,
        order_price=order_price,
        order_currency=currency,
        user_id=user_id,
        subscription_id=subscription_id
    )
    session.add(payment)
    await session.commit()


async def get_user_payments(
        session: AsyncSession,
        user_id: int
):
    stmt = select(Payment).where(Payment.user_id == user_id)
    result = await session.execute(stmt)
    payments = result.scalars()
    return payments

