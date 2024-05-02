from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.database import Order
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import OrderCreate

#async def create_order(session: AsyncSession, order_in: OrderCreate, owner_id: int):



