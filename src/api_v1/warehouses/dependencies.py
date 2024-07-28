from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import get_user_available_warehouse, get_user_own_warehouse
from src.api_v1.auth.dependencies import get_current_user
from src.exceptions import WarehouseDoesNotExist, PermissionDenied
from src.core.database import db_helper, User


async def get_warehouse_dependency(
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):
    warehouse = await get_user_available_warehouse(
        session=session,
        employee_id=user.id
    )
    if warehouse is None:
        raise WarehouseDoesNotExist()
    return warehouse


async def get_own_warehouse_dependency(
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):
    warehouse = await get_user_own_warehouse(
        session=session,
        owner_id=user.id
    )
    if warehouse is None:
        raise WarehouseDoesNotExist()
    return warehouse


