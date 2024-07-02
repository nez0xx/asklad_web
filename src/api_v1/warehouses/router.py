from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import User, Warehouse
from src.core.database.db_helper import db_helper
from . import crud, service
from fastapi.security import HTTPBearer
from src.api_v1.auth.dependencies import check_user_is_verify, get_current_user
from .crud import get_warehouse_by_name_and_owner, get_warehouse_by_id, get_employees
from .dependencies import get_own_warehouse_dependency, get_warehouse_dependency
from .schemas import WarehouseCreateSchema, WarehouseUpdateSchema

http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/warehouse",
    tags=["Warehouses"],
    dependencies=[Depends(http_bearer), Depends(check_user_is_verify)]
)

invite_router = APIRouter(
    prefix="/invite",
    tags=["Confirm invite"]
)


@invite_router.get(path="/{token}")
async def confirm_employee_invite(
        token: str,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    await service.confirm_employee_invite(
        session=session,
        token=token
    )


@router.get(path="/")
async def get_user_available_warehouse_view(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
    warehouse: Warehouse = Depends(get_warehouse_dependency)
):
    # не убирать(!)
    employees = await get_employees(session=session, warehouse_id=warehouse.id)

    data = {"warehouse": warehouse}

    if warehouse:
        if warehouse.owner_id == user.id:
            data["role"] = "own"
        else:
            data["role"] = "emp"

    return data


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
        employee_id: int,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        warehouse: Warehouse = Depends(get_own_warehouse_dependency)
):
    await service.send_employee_invite(
        session=session,
        employee_id=employee_id,
        warehouse=warehouse
    )


@router.patch(path="/")
async def change_wh_info(
        update_schema: WarehouseUpdateSchema,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        warehouse: Warehouse = Depends(get_own_warehouse_dependency)
):
    warehouse = await service.update_warehouse(
        session=session,
        warehouse=warehouse,
        schema=update_schema
    )

    return warehouse


@router.delete(path="/")
async def delete_warehouse(
    warehouse: Warehouse = Depends(get_own_warehouse_dependency),
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
):
    await service.delete_warehouse(
        session=session,
        warehouse=warehouse
    )


@router.delete(path="/employee")
async def delete_employee_view(
        employee_id: int,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user),
        warehouse: Warehouse = Depends(get_own_warehouse_dependency)
):
    await service.delete_employee(
        session=session,
        employee_id=employee_id,
        warehouse=warehouse
    )
