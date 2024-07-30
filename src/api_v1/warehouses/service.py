import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.warehouses import crud
from src.api_v1.auth.crud import get_user_by_id, get_user_by_email
from src.api_v1.utils import encode_jwt, decode_jwt
from src.api_v1.warehouses.crud import (
    get_employee_invite,
    create_employee_invite,
    add_employee,
    delete_employee_invite
)
from src.api_v1.warehouses.schemas import WarehouseCreateSchema, WarehouseUpdateSchema
from fastapi import HTTPException, status

from src.core.database import Warehouse, EmployeeInvite
from src.core.database.db_model_warehouse_employee_association import WarehouseEmployeeAssociation

from src.exceptions import WarehouseDoesNotExist, NotFound

from src.core.settings import settings

from sqlalchemy.exc import IntegrityError

from src.smtp import send_email


async def create_warehouse(session: AsyncSession, schema: WarehouseCreateSchema) -> Warehouse:
    warehouse = await crud.get_user_available_warehouse(
        session=session,
        employee_id=schema.owner_id
    )
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


async def send_employee_invite(session: AsyncSession, employee_email: str, warehouse: Warehouse):

    employee = await get_user_by_email(session, employee_email)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователя {employee_email} не существует"
        )

    employee_own_warehouse = await crud.get_user_available_warehouse(
        session=session,
        employee_id=employee.id
    )
    if employee_own_warehouse:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Пользователь уже работает на складе"
        )

    token = await create_employee_invite(
        session=session,
        employee_id=employee.id,
        warehouse_id=warehouse.id
    )
    invite_link = f"http://{settings.HOST}/invite/{token}"
    send_email(email_to=employee.email, html_message=invite_link, subject="Приглашение на склад")


async def confirm_employee_invite(session: AsyncSession, token: str):
    invite = await get_employee_invite(session=session, token=token)
    if invite is None:
        raise NotFound()

    now = datetime.now(tz=None) + timedelta(hours=3)
    if invite.expire_at < now:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Срок приглашения истёк"
        )

    employee_own_warehouse = await crud.get_user_available_warehouse(
        session=session,
        employee_id=invite.employee_id
    )
    if employee_own_warehouse:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Пользователь уже работает на складе"
        )

    await add_employee(
        session=session,
        employee_id=invite.employee_id,
        warehouse_id=invite.warehouse_id
    )
    await delete_employee_invite(session=session, token=token)


async def warehouse_info(session: AsyncSession, employee_id: int) -> Warehouse:
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


async def update_warehouse(session: AsyncSession, warehouse: Warehouse, schema: WarehouseUpdateSchema) -> Warehouse:
    if warehouse is None:
        raise WarehouseDoesNotExist()

    warehouse = await crud.update_warehouse(
        session=session,
        warehouse=warehouse,
        warehouse_update=schema
    )

    return warehouse


async def delete_warehouse(session: AsyncSession, warehouse: Warehouse):
    await crud.delete_warehouse(
        session=session,
        warehouse=warehouse
    )


