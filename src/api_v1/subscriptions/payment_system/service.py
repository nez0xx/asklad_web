import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Configuration, Payment

from src.api_v1.subscriptions.payment_system.crud import create_payment_model

Configuration.account_id = 435233
Configuration.secret_key = "test_m89h64uRzryHS4pc754-SMAdUzngt3i8a3vRc3faHKE"


async def create_payment(
        session: AsyncSession,
        value: int,
        currency: str,
        user_id: int,
        subscription_id: int
) -> str:

    payment = Payment.create({
        "amount": {
            "value": str(float(value)),
            "currency": currency.upper()
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://asklad.pro/"
        },
        "capture": True,
        "metadata": {
            "subscription_id": str(subscription_id)
        },
        "description": "Подписка"
    }, uuid.uuid4())

    payment_model = await create_payment_model(
        session=session,
        order_id=payment["id"],
        order_price=value,
        currency=currency,
        user_id=user_id,
        subscription_id=subscription_id
    )

    return payment["confirmation"]["confirmation_url"]
