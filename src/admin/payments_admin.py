from sqladmin import ModelView

from src.core.database import Payment


class PaymentAdmin(ModelView, model=Payment):
    column_list = [
        Payment.id,
        Payment.order_id,
        Payment.order_price,
        Payment.order_currency,
        Payment.created_at,
        Payment.subscription_id,
        Payment.payment_success,
        Payment.user_id,
        Payment.user_relationship

    ]
