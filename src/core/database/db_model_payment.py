from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.database import User, Subscription


class Payment(Base):
    order_id: Mapped[str]
    order_price: Mapped[int]
    order_currency: Mapped[str]
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id")
    )
    subscription_id: Mapped[int | None] = mapped_column(
        ForeignKey("subscriptions.id")
    )
    created_at: Mapped[datetime]

    payment_success: Mapped[bool] = mapped_column(
        default=False
    )

    user_relationship: Mapped["User"] = relationship(
        back_populates="payments_relationship"
    )
    # subscription: Mapped["Subscription"] = relationship(
    #     back_populates="payment"
    # )
