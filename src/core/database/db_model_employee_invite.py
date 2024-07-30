from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.core.database import User


class EmployeeInvite(Base):

    token: Mapped[str]

    warehouse_id: Mapped[int]

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    expire_at: Mapped[datetime]
