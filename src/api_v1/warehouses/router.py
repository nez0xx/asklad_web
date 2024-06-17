from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.auth.service import get_current_user
from src.core.database import User
from src.core.database.db_helper import db_helper
from . import crud, service
from fastapi.security import HTTPBearer
from src.api_v1.auth.dependencies import check_user_is_verify
from .crud import get_warehouse_by_name_and_owner, get_warehouse_by_id
from .schemas import WarehouseCreateSchema, EmployeeAddSchema, WarehouseUpdateSchema

http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/warehouse",
    tags=["Warehouses"],
    dependencies=[Depends(http_bearer), Depends(check_user_is_verify)]
)


@router.post(
    path="/"
)
async def create_warehouse_view(
        name: str,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):
    schema = WarehouseCreateSchema(name=name, owner_id=user.id)
    await service.create_warehouse(session=session, schema=schema)


@router.post(
    path="/employee"
)
async def add_employee_view(
        schema: EmployeeAddSchema,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):
    await service.add_employee(session=session, schema=schema, owner_id=user.id)


@router.get(
    path="/{warehouse_id}"
)
async def warehouse_info_view(
        warehouse_id: int,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):
    warehouse = await service.warehouse_info(
        session=session,
        employee_id=user.id,
        warehouse_id=warehouse_id
    )
    print(warehouse)
    return warehouse


@router.delete(path="/employee")
async def delete_employee_view(
        warehouse_id: int,
        employee_id: int,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):
    await service.delete_employee(
        session=session,
        employee_id=employee_id,
        owner_id=user.id,
        warehouse_id=warehouse_id
    )


@router.get(path="/")
async def get_user_warehouses_view(
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
    user: User = Depends(get_current_user)
):
    warehouses = await crud.get_user_warehouses(session=session, user_id=user.id)
    return warehouses


@router.patch(path="/")
async def change_wh_info(
        warehouse_id: int,
        update_schema: WarehouseUpdateSchema,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):
    warehouse = await service.update_warehouse(
        session=session,
        owner_id=user.id,
        warehouse_id=warehouse_id,
        schema=update_schema
    )

    return warehouse
