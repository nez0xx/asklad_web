from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import text, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from .db_model_user import User
    from .db_model_tariff import Tariff


class Subscription(Base):
    expired_at: Mapped[datetime]
    #price: Mapped[int]
    #paid_time: Mapped[datetime | None]
    started_at: Mapped[datetime] = mapped_column(
        default=datetime.now(),
        server_default=func.now()
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id")
    )
    #tariff_id: Mapped[str] = mapped_column(
    #    ForeignKey("tariffs.id")
    #)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )
    is_active: Mapped[bool] = mapped_column(
        default=False,
        server_default=text("false")
    )

    user_relationship: Mapped["User"] = relationship(
        back_populates="subscriptions_relationship"
    )

    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id"))

    tariff_relationship: Mapped["Tariff"] = relationship(
        back_populates="subscriptions_relationship"
    )


    def __str__(self):
        return f"{self.__class__.__name__} | {self.user}"

    def __repr__(self):
        return str(self)