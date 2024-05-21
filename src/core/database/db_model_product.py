from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
from src.core.database.db_model_order_product_association import ProductOrderAssociation


class Product(Base):

    __table_args__ = (
        UniqueConstraint(
            "atomy_id",
            "owner",
            name="idx_unique_atomy_id_owner",
        ),
    )

    atomy_id: Mapped[str]

    title: Mapped[str]

    amount: Mapped[int] = mapped_column(server_default='0')

    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))

    orders_details: Mapped[list["ProductOrderAssociation"]] = relationship(
        back_populates="product",
    )