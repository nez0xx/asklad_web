from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from src.core.database import Base

if TYPE_CHECKING:
    from src.core.database import Order


class Customer(Base):

    name: Mapped[str]

    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer_relationship"
    )

    id: Mapped[str] = mapped_column(primary_key=True)

    def __repr__(self):
        return self.name

