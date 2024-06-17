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

'''
@router.get(path="/")
async def get_product_view(
        warehouse_id: int,
        atomy_id: str,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):

    product = await service.get_product(
        session=session,
        atomy_id=atomy_id,
        employee_id=user.id,
        warehouse_id=warehouse_id
    )

    return product


@router.patch(path="/")
async def update_product_view(
        warehouse_id: int,
        atomy_id: str,
        product_schema: ProductUpdateSchema,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):

    product = await service.update_product(
        session=session,
        atomy_id=atomy_id,
        employee_id=user.id,
        warehouse_id=warehouse_id,
        schema=product_schema
    )

    return product
'''
