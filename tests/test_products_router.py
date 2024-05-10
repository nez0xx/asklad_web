'''
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.api_v1.auth.service import get_current_user
from .. import crud
from src.core.database import User
from src.core.database.db_helper import db_helper
from . import crud
from fastapi.security import HTTPBearer
from .schemas import ProductUpdate
from src.api_v1.auth.dependencies import check_user_is_verify

http_bearer = HTTPBearer()

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    dependencies=[Depends(http_bearer), Depends(check_user_is_verify)]
)


@router.get(
    path="/"
)
async def get_all_products_view(
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)

):
    products = await crud.get_all_products(session, user.id)
    return products


@router.get(path="/{id}")
async def get_product(
        id: str,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):

    product = await crud.get_product_by_id(
        session=session,
        id=id,
        owner_id=user.id
    )

    return product


@router.patch(path="/{id}")
async def update_product_view(
        id: str,
        product_schema: ProductUpdate,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):

    product = await crud.get_product_by_id(
        session=session,
        id=id,
        owner_id=user.id
    )
    product = await crud.update_product(
        session=session,
        product=product,
        product_update=product_schema
    )

    return product
'''
