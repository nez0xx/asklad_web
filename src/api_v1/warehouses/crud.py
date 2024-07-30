import uuid
from datetime import timedelta, datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from src.api_v1.warehouses.schemas import WarehouseCreateSchema, WarehouseUpdateSchema



from src.core.database import Warehouse, ProductOrderAssociation, Order, UnitedOrder, User, EmployeeInvite
from src.core.database.db_model_warehouse_employee_association import WarehouseEmployeeAssociation


async def get_employees(session: AsyncSession, warehouse_id: int) -> list[WarehouseEmployeeAssociation]:
    stmt = (select(WarehouseEmployeeAssociation)
            .options(selectinload(WarehouseEmployeeAssociation.employee_relationship))
            .where(WarehouseEmployeeAssociation.warehouse_id == warehouse_id))
    result = await session.execute(stmt)
    employees_details = result.scalars()
    return [elem for elem in employees_details]


async def get_warehouse_employee_association(
        session: AsyncSession,
        employee_id: int,
        warehouse_id: int
) -> WarehouseEmployeeAssociation:
    stmt = (select(WarehouseEmployeeAssociation)
            .where(WarehouseEmployeeAssociation.warehouse_id == warehouse_id)
            .where(WarehouseEmployeeAssociation.user_id == employee_id))
    result = await session.execute(stmt)
    employee_details = result.scalar_one_or_none()
    return employee_details


async def get_warehouse_by_name_and_owner(session: AsyncSession, name: str, owner_id: int) -> Warehouse:
    stmt = (select(Warehouse)
            .where(Warehouse.owner_id == owner_id)
            .where(Warehouse.name == name))
    result = await session.execute(stmt)
    warehouse = result.scalar_one_or_none()
    return warehouse


async def get_warehouse_by_id_and_owner(session: AsyncSession, warehouse_id: int, owner_id: int) -> Warehouse:
    stmt = (select(Warehouse)
            .where(Warehouse.owner_id == owner_id)
            .where(Warehouse.id == warehouse_id))
    result = await session.execute(stmt)
    warehouse = result.scalar_one_or_none()
    return warehouse


async def get_warehouse_by_id(session: AsyncSession, warehouse_id: int) -> Warehouse:
    stmt = (select(Warehouse)
            .options(selectinload(Warehouse.employees_details))
            .options(selectinload(Warehouse.orders_relationship))
            .options(selectinload(Warehouse.united_orders_relationship))
            .where(Warehouse.id == warehouse_id))

    result = await session.execute(stmt)
    warehouse = result.scalar_one_or_none()
    return warehouse


async def create_warehouse(session: AsyncSession, schema: WarehouseCreateSchema) -> Warehouse:
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


async def get_user_own_warehouse(session: AsyncSession, owner_id: int) -> Warehouse:
    stmt = select(Warehouse).where(Warehouse.owner_id == owner_id)
    result = await session.execute(stmt)
    warehouse = result.scalar_one_or_none()
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


async def delete_warehouse(session: AsyncSession, warehouse: Warehouse):
    from src.api_v1.orders.crud import get_united_orders, delete_united_order

    united_orders = await get_united_orders(
        session=session,
        warehouse_id=warehouse.id
    )

    united_orders_ids = [un_order.id for un_order in united_orders]

    for united_order_id in united_orders_ids:
        await delete_united_order(
            session=session,
            united_order_id=united_order_id
        )

    delete_employees_stmt = (delete(WarehouseEmployeeAssociation)
                            .where(WarehouseEmployeeAssociation.warehouse_id == warehouse.id))

    delete_warehouse_stmt = delete(Warehouse).where(Warehouse.id == warehouse.id)

    await session.execute(delete_employees_stmt)
    await session.execute(delete_warehouse_stmt)
    await session.commit()


async def create_employee_invite(session: AsyncSession, employee_id: int, warehouse_id: int) -> str:
    token = uuid.uuid4().hex
    expire_at = datetime.now() + timedelta(days=1)
    invite_model = EmployeeInvite(
        token=token,
        employee_id=employee_id,
        warehouse_id=warehouse_id,
        expire_at=expire_at
    )
    session.add(invite_model)
    await session.commit()
    return token


async def get_employee_invite(session: AsyncSession, token: str) -> EmployeeInvite | None:
    stmt = (select(EmployeeInvite)
            .where(EmployeeInvite.token == token))
    result = await session.execute(stmt)
    invite = result.scalar_one_or_none()
    return invite


async def delete_employee_invite(session: AsyncSession, token: str):
    stmt = delete(EmployeeInvite).where(EmployeeInvite.token == token)
    await session.execute(stmt)
