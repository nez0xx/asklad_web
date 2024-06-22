from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.warehouses import crud
from src.api_v1.auth.crud import get_user_by_email, get_user_by_id
from src.api_v1.warehouses.crud import get_warehouse_by_id
from src.api_v1.warehouses.schemas import WarehouseCreateSchema, WarehouseUpdateSchema
from fastapi import HTTPException, status

from src.api_v1.warehouses.utils import check_user_in_employees
from src.core.database import Warehouse
from src.core.database.db_model_warehouse_employee_association import WarehouseEmployeeAssociation

from src.api_v1.exceptions import WarehouseDoesNotExist


async def check_user_is_owner(session: AsyncSession, warehouse_id: int, owner_id: int):
    wh = await crud.get_warehouse_by_id_and_owner(session=session, warehouse_id=warehouse_id, owner_id=owner_id)
    if wh:
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not owner"
    )


async def create_warehouse(session: AsyncSession, schema: WarehouseCreateSchema):

    warehouse = await crud.get_user_available_warehouse(
        session=session,
        employee_id=schema.owner_id
    )
    print(warehouse)
    if warehouse:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already manage warehouse"
        )

    warehouse = await crud.create_warehouse(session=session, schema=schema)
    association = WarehouseEmployeeAssociation(user_id=schema.owner_id, warehouse_id=warehouse.id)
    session.add(association)
    await session.commit()
    return warehouse


async def add_employee(session: AsyncSession, employee_id: int, warehouse: Warehouse):
    employee = await get_user_by_id(session, employee_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {employee_id} doesn't exist"
        )

    if warehouse is None:
        raise WarehouseDoesNotExist()

    employee_own_warehouse = await crud.get_user_available_warehouse(
        session=session,
        employee_id=employee_id
    )

    if employee_own_warehouse:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with id {employee_id} already manage warehouse"
        )

    await crud.add_employee(
        session=session,
        employee_id=employee_id,
        warehouse_id=warehouse.id
    )


async def warehouse_info(session: AsyncSession, employee_id: int, warehouse_id: int):

    warehouse = await crud.get_user_available_warehouse(
        session=session,
        employee_id=employee_id
    )
    if warehouse is None:
        raise WarehouseDoesNotExist()
    return warehouse


async def delete_employee(session: AsyncSession, employee_id: int, warehouse: Warehouse):

    if warehouse is None:
        raise WarehouseDoesNotExist()

    if warehouse.owner_id == employee_id:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="You cannot delete yourself"
        )
    await crud.delete_employee(
        session=session,
        warehouse_id=warehouse.id,
        employee_id=employee_id
    )


async def update_warehouse(
        session: AsyncSession,
        warehouse: Warehouse,
        schema: WarehouseUpdateSchema
):
    if warehouse is None:
        raise WarehouseDoesNotExist()

    warehouse = await crud.update_warehouse(
        session=session,
        warehouse=warehouse,
        warehouse_update=schema
    )

    return warehouse


async def delete_warehouse(
        session: AsyncSession,
        warehouse: Warehouse
):
    await crud.delete_warehouse(
        session=session,
        warehouse=warehouse
    )


