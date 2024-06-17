from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.warehouses import crud
from src.api_v1.auth.crud import get_user_by_email, get_user_by_id
from src.api_v1.warehouses.crud import get_warehouse_by_id
from src.api_v1.warehouses.schemas import WarehouseCreateSchema, EmployeeAddSchema, WarehouseUpdateSchema
from fastapi import HTTPException, status

from src.api_v1.warehouses.utils import check_user_in_employees
from src.core.database.db_model_warehouse_employee_association import WarehouseEmployeeAssociation


async def check_user_is_owner(session: AsyncSession, warehouse_id: int, owner_id: int):
    wh = await crud.get_warehouse_by_id_and_owner(session=session, warehouse_id=warehouse_id, owner_id=owner_id)
    if wh:
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not owner"
    )


async def create_warehouse(session: AsyncSession, schema: WarehouseCreateSchema):

    warehouse = await crud.get_warehouse_by_name_and_owner(
        session=session,
        **schema.model_dump()
    )

    if warehouse:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already manage warehouse with same name"
        )

    warehouse = await crud.create_warehouse(session=session, schema=schema)
    association = WarehouseEmployeeAssociation(user_id=schema.owner_id, warehouse_id=warehouse.id)
    session.add(association)
    await session.commit()
    return warehouse


async def add_employee(session: AsyncSession, schema: EmployeeAddSchema, owner_id: int):
    employee = await get_user_by_id(session, schema.employee_id)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {schema.employee_id} doesn't exist"
        )

    warehouse = await crud.get_warehouse_by_id_and_owner(
        session=session,
        warehouse_id=schema.warehouse_id,
        owner_id=owner_id
    )

    if warehouse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse with name {schema.warehouse_name} doesn't exist"
        )

    association = WarehouseEmployeeAssociation(user_id=employee.id, warehouse_id=warehouse.id)
    session.add(association)
    await session.commit()


async def warehouse_info(session: AsyncSession, employee_id: int, warehouse_id: int):
    await check_user_in_employees(
        session=session,
        warehouse_id=warehouse_id,
        employee_id=employee_id
    )
    warehouse = await get_warehouse_by_id(session=session, warehouse_id=warehouse_id)
    print(warehouse, "sfsfsfsfsfsf")
    return warehouse


async def delete_employee(session: AsyncSession, warehouse_id: int, employee_id: int, owner_id: int):
    await check_user_is_owner(session=session, warehouse_id=warehouse_id, owner_id=owner_id)
    if owner_id == employee_id:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="You cannot delete yourself"
        )
    await crud.delete_employee(session=session, warehouse_id=warehouse_id, employee_id=employee_id)


async def update_warehouse(
        session: AsyncSession,
        owner_id: int,
        warehouse_id: int,
        schema: WarehouseUpdateSchema
):
    await check_user_is_owner(
        session=session,
        owner_id=owner_id,
        warehouse_id=warehouse_id
    )

    warehouse = await crud.get_warehouse_by_id(
        session=session,
        warehouse_id=warehouse_id
    )

    if warehouse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Warehouse with id {warehouse_id} does not exist"
        )

    warehouse = await crud.update_warehouse(
        session=session,
        warehouse=warehouse,
        warehouse_update=schema
    )

    return warehouse


