from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr
from src.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.database.db_model_order import Order


class UnitedOrder(Base):

    @declared_attr.directive
    def __tablename__(cls):
        return "united_orders"

    id: Mapped[str] = mapped_column(unique=True, primary_key=True)

    warehouse_id: Mapped[int]

    orders_relationship: Mapped[list["Order"]] = relationship(back_populates="united_order_relationship")

    delivery_date: Mapped[datetime] = mapped_column(
        nullable=True
    )

    delivered: Mapped[bool] = mapped_column(default=False)


