from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.warehouses import crud
from src.api_v1.auth.crud import get_user_by_id
from src.api_v1.utils import encode_jwt, decode_jwt
from src.api_v1.warehouses.schemas import WarehouseCreateSchema, WarehouseUpdateSchema
from fastapi import HTTPException, status

from src.api_v1.warehouses.utils import check_user_in_employees
from src.core.database import Warehouse
from src.core.database.db_model_warehouse_employee_association import WarehouseEmployeeAssociation

from src.api_v1.exceptions import WarehouseDoesNotExist

from src.core.settings import settings
from src.smtp import send_email

from sqlalchemy.exc import IntegrityError


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


async def send_employee_invite(session: AsyncSession, employee_id: int, warehouse: Warehouse):
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

    token = encode_jwt(
        payload={
            "employee_id": employee_id,
            "warehouse_id": warehouse.id
        },
        expire_minutes=60*24*3
    )
    invite_link = f"http://{settings.HOST}/invite/{token}"
    print(invite_link)
    #send_message(email_to=employee.email, html_message=invite_link, subject="Invite to warehouse")


async def confirm_employee_invite(
        session: AsyncSession,
        token: str
):
    data = decode_jwt(token)

    try:
        await crud.add_employee(
            session=session,
            employee_id=data["employee_id"],
            warehouse_id=data["warehouse_id"]
        )
    except IntegrityError as e:
        print(IntegrityError)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invite has already been accepted"
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


