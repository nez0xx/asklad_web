from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api_v1.warehouses.schemas import WarehouseCreateSchema, WarehouseUpdateSchema

from src.api_v1.orders.crud import get_united_orders

from src.core.database import Warehouse, ProductOrderAssociation, Order, UnitedOrder
from src.core.database.db_model_warehouse_employee_association import WarehouseEmployeeAssociation


async def get_employees(session: AsyncSession, warehouse_id: int):
    stmt = (select(WarehouseEmployeeAssociation)
            .where(WarehouseEmployeeAssociation.warehouse_id == warehouse_id))
    result = await session.execute(stmt)
    employees_details = result.scalars()
    return employees_details


async def get_warehouse_employee_association(session: AsyncSession, employee_id: int, warehouse_id: int):
    stmt = (select(WarehouseEmployeeAssociation)
            .where(WarehouseEmployeeAssociation.warehouse_id == warehouse_id)
            .where(WarehouseEmployeeAssociation.user_id == employee_id))
    result = await session.execute(stmt)
    employee_details = result.scalar_one_or_none()
    return employee_details


async def get_warehouse_by_name_and_owner(session: AsyncSession, name: str, owner_id: int):
    stmt = (select(Warehouse)
            .where(Warehouse.owner_id == owner_id)
            .where(Warehouse.name == name))
    result = await session.execute(stmt)
    warehouse = result.scalar_one_or_none()
    return warehouse


async def get_warehouse_by_id_and_owner(session: AsyncSession, warehouse_id: int, owner_id: int):
    stmt = (select(Warehouse)
            .where(Warehouse.owner_id == owner_id)
            .where(Warehouse.id == warehouse_id))
    result = await session.execute(stmt)
    warehouse = result.scalar_one_or_none()
    return warehouse


async def get_warehouse_by_id(session: AsyncSession, warehouse_id: int):
    stmt = (select(Warehouse)
            .options(selectinload(Warehouse.employees_details))
            .options(selectinload(Warehouse.orders_relationship))
            .where(Warehouse.id == warehouse_id))
    result = await session.execute(stmt)
    warehouse = result.scalar_one_or_none()
    return warehouse


async def create_warehouse(session: AsyncSession, schema: WarehouseCreateSchema):
    warehouse = Warehouse(**schema.model_dump())
    session.add(warehouse)
    await session.commit()
    return warehouse


async def add_employee(session: AsyncSession, employee_id: int, warehouse_id: int):
    session.add(WarehouseEmployeeAssociation(
        user_id=employee_id,
        warehouse_id=warehouse_id
    ))
    await session.commit()


async def delete_employee(session: AsyncSession, employee_id: int, warehouse_id: int):
    stmt = (delete(WarehouseEmployeeAssociation)
            .where(WarehouseEmployeeAssociation.user_id == employee_id)
            .where(WarehouseEmployeeAssociation.warehouse_id == warehouse_id))
    result = await session.execute(stmt)
    await session.commit()
    return result


async def get_user_own_warehouse(session: AsyncSession, owner_id: int):
    stmt = select(Warehouse).where(Warehouse.owner_id == owner_id)
    result = await session.execute(stmt)
    warehouse = result.scalar_one_or_none()
    print(warehouse)
    return warehouse


async def get_user_available_warehouse(session: AsyncSession, employee_id: int) -> Warehouse | None:
    stmt = (select(WarehouseEmployeeAssociation)
            .where(WarehouseEmployeeAssociation.user_id == employee_id))

    result = await session.execute(stmt)
    association = result.scalar_one_or_none()
    if association:
        warehouse = await get_warehouse_by_id(
            session=session,
            warehouse_id=association.warehouse_id
        )
        return warehouse

    return None


async def update_warehouse(
    session: AsyncSession,
    warehouse: Warehouse,
    warehouse_update: WarehouseUpdateSchema
) -> Warehouse:
    for name, value in warehouse_update.model_dump(exclude_unset=True).items():
        setattr(warehouse, name, value)
    await session.commit()
    return warehouse


# функция дублирует код функций из orders.crud и выглядит некрасиво,
# потому что при импорте получается циклический импорт
async def delete_warehouse(
    session: AsyncSession,
    warehouse: Warehouse
):

    get_united_orders_stmt = (select(UnitedOrder)
            .where(UnitedOrder.warehouse_id == warehouse.id))

    result = await session.execute(get_united_orders_stmt)

    united_orders = result.scalars().all()

    united_orders_ids = [un_order.id for un_order in united_orders]

    for united_order_id in united_orders_ids:

        get_products_stmt = (select(ProductOrderAssociation.id)
                             .join(Order)
                             .where(Order.united_order_id == united_order_id))

        result = await session.execute(get_products_stmt)
        ids = [elem[0] for elem in result.all()]

        delete_products_stmt = delete(ProductOrderAssociation).where(ProductOrderAssociation.id.in_(ids))
        delete_orders_stmt = delete(Order).where(Order.united_order_id == united_order_id)
        delete_united_order_stmt = delete(UnitedOrder).where(UnitedOrder.id == united_order_id)

        await session.execute(delete_products_stmt)
        await session.execute(delete_orders_stmt)
        await session.execute(delete_united_order_stmt)
        await session.commit()

    delete_employees_stmt = (delete(WarehouseEmployeeAssociation)
                            .where(WarehouseEmployeeAssociation.warehouse_id == warehouse.id))

    delete_warehouse_stmt = delete(Warehouse).where(Warehouse.id == warehouse.id)

    await session.execute(delete_employees_stmt)
    await session.execute(delete_warehouse_stmt)
    await session.commit()



