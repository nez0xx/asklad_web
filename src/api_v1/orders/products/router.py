from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.auth.service import get_current_user
from .. import crud
from src.core.database import User
from src.core.database.db_helper import db_helper
from . import crud, service
from fastapi.security import HTTPBearer
from .schemas import ProductUpdateSchema
from src.api_v1.auth.dependencies import check_user_is_verify

http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(http_bearer), Depends(check_user_is_verify)]
)


@router.get(
    path="/all"
)
async def get_all_products_view(
        warehouse_id: int,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)

):
    products = await service.products_list(
        session=session,
        warehouse_id=warehouse_id,
        employee_id=user.id
    )

    return products


@router.patch(
    path="/change_amount"
)
async def change_product_amount_view(
        order_id: str,
        product_id: str,
        amount: int,
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):
    await service.change_product_amount(
        session=session,
        order_id=order_id,
        product_id=product_id,
        amount=amount
    )
