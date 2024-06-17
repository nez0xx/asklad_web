from datetime import datetime, timezone

from sqlalchemy import String, text, func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.database import Base
from src.core.database.db_model_warehouse_employee_association import WarehouseEmployeeAssociation

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .db_model_order import Order

class Warehouse(Base):

    name: Mapped[str]

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    employees_details: Mapped[list["WarehouseEmployeeAssociation"]] = relationship(
        back_populates="warehouse",
    )

    orders_relationship: Mapped[list["Order"]] = relationship()

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(tz=timezone.utc),
        server_default=func.now()
    )