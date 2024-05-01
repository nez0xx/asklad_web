from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from core.database import Base
from .db_model_order_product_association import ProductOrderAssociation

if TYPE_CHECKING:
    from core.database import Customer, Product

class Order(Base):

    customer: Mapped[int] = mapped_column(ForeignKey("customers.id"))

    customer_relationship: Mapped["Customer"] = relationship(
        back_populates="orders"
    )

    customer_phone: Mapped[str]

    owner: Mapped[int] = mapped_column(ForeignKey("users.id"))

    products: Mapped[list["Product"]] = relationship(
        secondary="product_order_association",
        back_populates="orders",
    )

    products_details: Mapped[list["ProductOrderAssociation"]] = relationship(
        back_populates="order"
    )