from typing import TYPE_CHECKING

from datetime import datetime, timezone

from sqlalchemy import String, text, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.core.database import Base
from src.core.database.db_model_warehouse_employee_association import WarehouseEmployeeAssociation

if TYPE_CHECKING:
    from src.core.database import Subscription, UnitedOrder


class User(Base):
    hashed_password: Mapped[str]
    email: Mapped[str] = mapped_column(
        String(length=40),
        unique=True
    )

    name: Mapped[str]

    is_admin: Mapped[bool] = mapped_column(
        default=False,
        server_default=text("false")
    )

    is_verify: Mapped[bool] = mapped_column(
        default=False,
        server_default=text("false")
    )

    warehouses_details: Mapped[list["WarehouseEmployeeAssociation"]] = relationship(back_populates="employee_relationship")

    subscriptions_relationship: Mapped[list["Subscription"]] = relationship(back_populates="user_relationship")

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now()

    )

    # выданные юзером заказы
    united_orders_relationship: Mapped[list["UnitedOrder"]] = relationship(back_populates="employee_relationship")

    def __repr__(self):
        return f"{self.name} {self.email}"
