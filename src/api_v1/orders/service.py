from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.orders.crud import get_order_by_id, create_order, create_united_order
from src.api_v1.orders.customers.crud import get_or_create_customer
from src.api_v1.orders.schemas import OrderBase, UnitedOrderSchema
from src.api_v1.warehouses.utils import check_user_in_employees


async def add_orders(session: AsyncSession, united_order_schema: UnitedOrderSchema, employee_id: int):

    await check_user_in_employees(
        session=session,
        employee_id=employee_id,
        warehouse_id=united_order_schema.warehouse_id
    )

    for order_schema in united_order_schema.orders:

        order = await get_order_by_id(
            session=session,
            id=order_schema.atomy_id,
            warehouse_id=united_order_schema.warehouse_id
        )

        if order:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Order with id {order_schema.atomy_id} already exists"
            )

        customer = await get_or_create_customer(
            session=session,
            customer_schema=order_schema.customer,
            warehouse_id=united_order_schema.warehouse_id
        )

        await create_order(
            session,
            customer_id=customer.id,
            order_schema=order_schema,
            united_order_id=united_order_schema.united_order_id,
            warehouse_id=united_order_schema.warehouse_id
        )

    await create_united_order(session, united_order_schema.united_order_id)

    return united_order_schema.united_order_id
