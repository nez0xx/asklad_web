from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.warehouses import crud
from src.api_v1.auth.crud import get_user_by_email
from src.api_v1.warehouses.schemas import WarehouseCreateSchema, EmployeeAddSchema
from fastapi import HTTPException, status

from src.core.database import Warehouse
from src.core.database.db_model_warehouse_employee_association import WarehouseEmployeeAssociation


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

    return warehouse


async def add_employee(session: AsyncSession, schema: EmployeeAddSchema, owner_id: int):
    employee = await get_user_by_email(session, schema.email)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {schema.email} doesn't exist"
        )

    warehouse = await crud.get_warehouse_by_name_and_owner(
        session=session,
        name=schema.warehouse_name,
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
