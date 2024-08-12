from datetime import date, datetime

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, declared_attr

from typing import TYPE_CHECKING

from src.core.database import Base

if TYPE_CHECKING:
    from src.core.database import Warehouse, User, Order


class UnitedOrder(Base):

    @declared_attr.directive
    def __tablename__(cls):
        return "united_orders"

    id: Mapped[str] = mapped_column(unique=True, primary_key=True)

    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))

    warehouse_relationship: Mapped["Warehouse"] = relationship(back_populates="united_orders_relationship")

    orders_relationship: Mapped[list["Order"]] = relationship(back_populates="united_order_relationship")

    delivery_date: Mapped[date] = mapped_column(
        nullable=True
    )
    # работник который принял доставку
    accepted_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    # работник который принял доставку
    employee_relationship: Mapped["User"] = relationship(back_populates="united_orders_relationship")

    delivered: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now
    )

    def __repr__(self):
        return f"{self.id}"

