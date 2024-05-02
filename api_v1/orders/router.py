from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api_v1.auth.service import get_current_user
from api_v1.orders import crud
from api_v1.orders.schemas import OrderCreate
from core.database import User
from core.database.db_helper import db_helper
from .products.crud import get_all_products
from fastapi.security import HTTPBearer

http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    dependencies=[Depends(http_bearer)]
)


@router.post(
    path="/create_order"
)
async def create_order_view(
        order_schema: OrderCreate,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)

):
    order = await crud.create_order(session, order_schema, owner_id=user.id)
    return order

@router.get(
    path="/products"
)
async def create_order_view(
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)

):
    products = await get_all_products(session, user.id)
    return products


