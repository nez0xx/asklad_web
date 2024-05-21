from datetime import datetime, timezone

from sqlalchemy import String, text, func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.database import Base
from src.core.database.db_model_warehouse_employee_association import WarehouseEmployeeAssociation


class Warehouse(Base):

    name: Mapped[str]

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    employees_details: Mapped[list["WarehouseEmployeeAssociation"]] = relationship(
        back_populates="warehouses",
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(tz=timezone.utc),
        server_default=func.now()
    )