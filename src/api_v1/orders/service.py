from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.orders.crud import get_order_by_id, create_order
from src.api_v1.orders.schemas import OrderBase
from src.api_v1.warehouses.crud import get_warehouse_employee_association


async def check_user_in_employees(session: AsyncSession, employee_id: int, warehouse_id: int, auto_error=True) -> bool:

    association = get_warehouse_employee_association(
        session=session,
        user_id=employee_id,
        warehouse_id=warehouse_id
    )
    if (association is None) and auto_error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You not in employees list")

    return association is not None


async def add_order(session: AsyncSession, order_schema: OrderBase, employee_id: int):

    await check_user_in_employees(
        session=session,
        employee_id=employee_id,
        warehouse_id=order_schema.warehouse_id
    )

    order = await get_order_by_id(
        session=session,
        id=order_schema.atomy_id,
        warehouse_id=order_schema.warehouse_id
    )

    if order:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Order with id {order_schema.atomy_id} already exists"
        )

    order_id = await create_order(session, order_schema)

    return order_id
