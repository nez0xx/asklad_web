from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base

if TYPE_CHECKING:
    from src.core.database import User


class EmailConfirmToken(Base):
    __tablename__ = "email_confirm_tokens"

    token: Mapped[str]

    created_at: Mapped[datetime]

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    user_relationship: Mapped["User"] = relationship(back_populates="email_confirm_token")
