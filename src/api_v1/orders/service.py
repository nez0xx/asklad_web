from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.orders.crud import get_order_by_id, create_order
from src.api_v1.orders.schemas import OrderCreate


async def add_order(session: AsyncSession, order_schema: OrderCreate, owner_id: int):

    order = await get_order_by_id(session, id=order_schema.id, owner_id=owner_id)
    if order:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Order with id {order_schema.id} already exists"
        )

    order_id = await create_order(session, order_schema, owner_id=owner_id)

    return order_id
