from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
from src.core.database.db_model_order_product_association import ProductOrderAssociation


class Product(Base):

    id: Mapped[str] = mapped_column(primary_key=True)

    title: Mapped[str]

    price: Mapped[int] = mapped_column(default=0)

    pv: Mapped[int] = mapped_column(default=0)

    orders_details: Mapped[list["ProductOrderAssociation"]] = relationship(
        back_populates="product_relationship",
    )

    def __repr__(self):
        return f"{self.id} {self.title}"
