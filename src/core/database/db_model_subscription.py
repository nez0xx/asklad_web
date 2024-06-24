from datetime import datetime, timezone, timedelta

from sqlalchemy import text, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import User, Base


class Subscription(Base):
    expired_at: Mapped[datetime]
    #price: Mapped[int]
    #paid_time: Mapped[datetime | None]
    started_at: Mapped[datetime] = mapped_column(
        default=datetime.now(tz=timezone(offset=timedelta(hours=5))),
        server_default=func.now()
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id")
    )
    #tariff_id: Mapped[str] = mapped_column(
    #    ForeignKey("tariffs.id")
    #)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(tz=timezone(offset=timedelta(hours=5))),
        server_default=func.now(),
    )
    is_active: Mapped[bool] = mapped_column(
        default=False,
        server_default=text("false")
    )

    user: Mapped["User"] = relationship(
        back_populates="subscriptions"
    )
    ''''
    paypal_payment: Mapped["PayPalPayment"] = relationship(
        back_populates="subscription"
    )
    freekassa_payment_relationship: Mapped["FreekassaPayment"] = relationship(
        back_populates="subscription_relationship"
    )
    tariff: Mapped["Tariff"] = relationship(
        backref="subscription"
    )
    '''

    def __str__(self):
        return f"{self.__class__.__name__} | {self.user}"

    def __repr__(self):
        return str(self)