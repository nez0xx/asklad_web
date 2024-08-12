from datetime import date, datetime

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from src.core.database import Base
from .db_model_order_product_association import ProductOrderAssociation

if TYPE_CHECKING:
    from src.core.database import (Customer,
                                   UnitedOrder,
                                   User)


class Order(Base):

    id: Mapped[str] = mapped_column(primary_key=True)

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))

    customer_relationship: Mapped["Customer"] = relationship(
        back_populates="orders"
    )

    customer_phone: Mapped[str]

    customer_name: Mapped[str]

    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))

    united_order_id: Mapped[str] = mapped_column(ForeignKey("united_orders.id"))

    united_order_relationship: Mapped["UnitedOrder"] = relationship(back_populates="orders_relationship")

    is_given_out: Mapped[bool] = mapped_column(
        default=False,
        server_default=text("false")
    )

    products_details: Mapped[list["ProductOrderAssociation"]] = relationship(
        back_populates="order_relationship"
    )

    issue_date: Mapped[date] = mapped_column(nullable=True)

    given_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)  # кем выдан

    given_by_relationship: Mapped["User"] = relationship(back_populates="")

    comment: Mapped[str] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now
    )

    def __repr__(self):
        return f"{self.id}_{self.customer_name.split()[0]}"
