from typing import TYPE_CHECKING

from datetime import datetime, timezone

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base

if TYPE_CHECKING:
    pass


class EmailConfirmToken(Base):
    __tablename__ = "email_confirm_tokens"

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(tz=timezone.utc),
        server_default=func.now()
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True
    )

