from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.auth.service import get_current_user
from src.core.database import User
from src.core.database.db_helper import db_helper
from . import crud, service
from fastapi.security import HTTPBearer
from src.api_v1.auth.dependencies import check_user_is_verify
from .schemas import WarehouseCreateSchema, EmployeeAddSchema

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



