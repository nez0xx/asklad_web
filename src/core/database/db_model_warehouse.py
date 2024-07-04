from datetime import date

from sqlalchemy import String, text, func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.database import Base
from src.core.database.db_model_warehouse_employee_association import WarehouseEmployeeAssociation

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .db_model_order import Order
    from .db_model_united_order import UnitedOrder


class Warehouse(Base):

    name: Mapped[str]

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    employees_details: Mapped[list["WarehouseEmployeeAssociation"]] = relationship(
        back_populates="warehouse_relationship",
    )

    orders_relationship: Mapped[list["Order"]] = relationship()

    united_orders_relationship: Mapped[list["UnitedOrder"]] = relationship(back_populates="warehouse_relationship")

    created_at: Mapped[date] = mapped_column(
        default=date.today(),
        server_default=func.now()
    )

    def __repr__(self):
        return f"Id: {self.id}; {self.name}"
