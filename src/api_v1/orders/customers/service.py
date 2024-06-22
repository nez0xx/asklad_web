from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.orders.customers.crud import get_warehouse_customers
from src.api_v1.warehouses.crud import get_user_available_warehouse


async def get_all_customers(session: AsyncSession, user_id: int):
    warehouse = await get_user_available_warehouse(session=session, employee_id=user_id)
    all_customers = []

    warehouse_customers = await get_warehouse_customers(session=session, warehouse_id=warehouse.id)
    all_customers.extend(warehouse_customers)

    return all_customers
