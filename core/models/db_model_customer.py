from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from core.models import Base

if TYPE_CHECKING:
    from core.models import Order

class Customer(Base):

    name: Mapped[str]

    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer_relationship"
    )

    atomy_id: Mapped[int]

    owner: Mapped[int] = mapped_column(ForeignKey("users.id"))