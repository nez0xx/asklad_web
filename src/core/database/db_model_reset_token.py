from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base
from src.core.database.db_model_order_product_association import ProductOrderAssociation

if TYPE_CHECKING:
    from src.core.database import User


class ResetToken(Base):

    token: Mapped[str]

    expired_at: Mapped[datetime]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
