from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from core.database import Base, Order
from core.database.db_model_order_product_association import ProductOrderAssociation


class Product(Base):

    __table_args__ = (
        UniqueConstraint(
            "atomy_id",
            "owner",
            name="idx_unique_id_owner",
        ),
    )

    title: Mapped[str]

    atomy_id: Mapped[int]

    amount: Mapped[int] = mapped_column(server_default='0')

    owner: Mapped[int] = mapped_column(ForeignKey("users.id"))

    orders: Mapped[list["Order"]] = relationship(
        secondary="product_order_association",
        back_populates="products",
    )

    orders_details: Mapped[list["ProductOrderAssociation"]] = relationship(
        back_populates="product",
    )