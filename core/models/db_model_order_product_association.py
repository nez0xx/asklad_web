from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db_model_base import Base


if TYPE_CHECKING:
    from core.models import Product, Order


class ProductOrderAssociation(Base):

    __tablename__ = "product_order_association"

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "order_id",
            name="idx_unique_product_order",
        ),
    )

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))

    order: Mapped["Order"] = relationship(
        back_populates="products_details",
    )
    # association between Assocation -> Product
    product: Mapped["Product"] = relationship(
        back_populates="orders_details",
    )