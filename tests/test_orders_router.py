'''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.auth.service import get_current_user
from src.api_v1.orders import crud
from src.api_v1.orders.schemas import OrderCreate
from src.core.database import User
from src.core.database.db_helper import db_helper
from fastapi.security import HTTPBearer
from src.api_v1.auth.dependencies import check_user_is_verify


http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    dependencies=[Depends(http_bearer), Depends(check_user_is_verify)]
)




@router.get(path="/")
async def get_orders(
        is_given_out: bool | None = None,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):

    orders = await crud.get_all_orders(
        session=session,
        owner_id=user.id,
        is_given_out=is_given_out
    )

    return orders


@router.post(
    path="/create_order"
)
async def create_order_view(
        order_schema: OrderCreate,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)

):
    order_id = await crud.create_order(session, order_schema, owner_id=user.id)

    return {"The created order id": order_id}




@router.post(path="/give_out")
async def give_order_out(
        order_id: str,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)
):
    order = await crud.give_out(
        session=session,
        order_id=order_id,
        owner_id=user.id
    )

    if order:
        return order

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"order with id={order_id} not exists"
        )



@router.get(path="/{id}")
async def get_order(
    id: str,
    session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
    user: User = Depends(get_current_user)
):
    order = await crud.get_order_by_id(
        session=session,
        id=id,
        owner_id=user.id
    )
    return order

'''

