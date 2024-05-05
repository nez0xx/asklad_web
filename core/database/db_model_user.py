from datetime import datetime, timezone

from sqlalchemy import String, text, func
from sqlalchemy.orm import mapped_column, Mapped, relationship

from core.database import Base
from core.database.db_model_email_confirm_token import EmailConfirmToken


class User(Base):
    hashed_password: Mapped[str]
    email: Mapped[str] = mapped_column(
        String(length=40),
        unique=True
    )

    is_admin: Mapped[bool] = mapped_column(
        default=False,
        server_default=text("false")
    )

    is_verify: Mapped[bool] = mapped_column(
        default=False,
        server_default=text("false")
    )


    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(tz=timezone.utc),
        server_default=func.now()
    )