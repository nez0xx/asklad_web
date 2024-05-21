from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from src.core.database import Base

if TYPE_CHECKING:
    from src.core.database import Order


class Customer(Base):

    __table_args__ = (
        UniqueConstraint(
            "atomy_id",
            "warehouse_id",
            name="idx_unique_atomy_id_warehouse_id",
        ),
    )

    name: Mapped[str]

    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer_relationship"
    )

    atomy_id: Mapped[str]

    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"))
