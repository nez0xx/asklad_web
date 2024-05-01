from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from core.models import Base, Order
from core.models.db_model_order_product_association import ProductOrderAssociation


class Product(Base):

    title: Mapped[str]

    amount: Mapped[int]

    owner: Mapped[int] = mapped_column(ForeignKey("users.id"))

    orders: Mapped[list["Order"]] = relationship(
        secondary="product_order_association",
        back_populates="products",
    )

    orders_details: Mapped[list["ProductOrderAssociation"]] = relationship(
        back_populates="product",
    )