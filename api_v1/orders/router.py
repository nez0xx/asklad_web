from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.orders import crud
from api_v1.orders.schemas import OrderCreate
from core.database.db_helper import db_helper

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post(
    path="/create_order"
)
def create_order_view(
        order: OrderCreate,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),

):
    return {"o":order}

