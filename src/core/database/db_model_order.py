from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from src.core.database import Base
from .db_model_order_product_association import ProductOrderAssociation

if TYPE_CHECKING:
    from src.core.database import (Customer,
                                   UnitedOrder)


class Order(Base):

    id: Mapped[str] = mapped_column(primary_key=True)

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))

    customer_relationship: Mapped["Customer"] = relationship(
        back_populates="orders"
    )

    customer_phone: Mapped[str]

    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))

    united_order_id: Mapped[str] = mapped_column(ForeignKey("united_orders.id"))

    united_order_relationship: Mapped["UnitedOrder"] = relationship(back_populates="orders_relationship")

    is_given_out: Mapped[bool] = mapped_column(
        default=False,
        server_default=text("false")
    )

    products_details: Mapped[list["ProductOrderAssociation"]] = relationship(
        back_populates="order"
    )

    #given_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
