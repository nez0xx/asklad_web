from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db_model_base import Base


if TYPE_CHECKING:
    from src.core.database import User, Warehouse


class WarehouseEmployeeAssociation(Base):

    __tablename__ = "warehouse_employee_association"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "warehouse_id",
            name="idx_unique_user_warehouse",
        ),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    warehouse_id: Mapped[str] = mapped_column(ForeignKey("warehouses.id"))

    employee_relationship: Mapped["User"] = relationship(
        back_populates="warehouses_details",
    )
    # association between Assocation -> Product
    warehouse_relationship: Mapped["Warehouse"] = relationship(
        back_populates="employees_details",
    )

    def __repr__(self):
        return f"Wh: {self.warehouse_id} Emp: {self.user_id}"
