from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from src.core.database import Base, Subscription

if TYPE_CHECKING:
    from .db_model_subscription import Subscription


class Tariff(Base):
    tariff_name: Mapped[str]

    price_rub: Mapped[int] = mapped_column(default=0)
    price_byn: Mapped[int] = mapped_column(default=0)
    price_kzt: Mapped[int] = mapped_column(default=0)

    expire_days: Mapped[int]

    subscriptions_relationship: Mapped[list["Subscription"]] = relationship(back_populates="tariff_relationship")
