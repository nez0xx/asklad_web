from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api_v1.warehouses.schemas import WarehouseCreateSchema, EmployeeAddSchema, WarehouseUpdateSchema
from src.core.database import Warehouse
from src.core.database.db_model_warehouse_employee_association import WarehouseEmployeeAssociation


async def get_employees(session: AsyncSession, warehouse_id: int):
    stmt = (select(WarehouseEmployeeAssociation)
            .where(WarehouseEmployeeAssociation.warehouse_id == warehouse_id))
    result = await session.execute(stmt)
    employees_details = result.scalars()
    return employees_details


async def get_warehouse_employee_association(session: AsyncSession, user_id: int, warehouse_id: int):
    stmt = (select(WarehouseEmployeeAssociation)
            .where(WarehouseEmployeeAssociation.warehouse_id == warehouse_id)
            .where(WarehouseEmployeeAssociation.user_id == user_id))
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


async def add_employee(session: AsyncSession, schema: EmployeeAddSchema):
    session.add(WarehouseEmployeeAssociation(
        user_id=schema.user_id,
        warehouse_id=schema.warehouse_id
    ))


async def delete_employee(session: AsyncSession, employee_id: int, warehouse_id: int):
    stmt = (delete(WarehouseEmployeeAssociation)
            .where(WarehouseEmployeeAssociation.user_id == employee_id)
            .where(WarehouseEmployeeAssociation.warehouse_id == warehouse_id))
    result = await session.execute(stmt)
    await session.commit()
    return result


async def get_user_warehouses(session: AsyncSession, user_id: int):
    stmt = select(Warehouse).where(Warehouse.owner_id == user_id)
    result = await session.execute(stmt)
    warehouses = result.scalars().all()
    print(warehouses)
    return warehouses


async def update_warehouse(
    session: AsyncSession,
    warehouse: Warehouse,
    warehouse_update: WarehouseUpdateSchema
) -> Warehouse:
    for name, value in warehouse_update.model_dump(exclude_unset=True).items():
        setattr(warehouse, name, value)
    await session.commit()
    return warehouse



