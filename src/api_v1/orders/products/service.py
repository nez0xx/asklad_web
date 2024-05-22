from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.orders.products import crud
from src.api_v1.orders.products.schemas import ProductUpdateSchema
from src.api_v1.warehouses.utils import check_user_in_employees


exc404 = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with this id does not exist in the warehouse"
        )


async def get_product(
        session: AsyncSession,
        atomy_id: str,
        warehouse_id: int,
        employee_id
):

    await check_user_in_employees(
        session=session,
        employee_id=employee_id,
        warehouse_id=warehouse_id
    )

    product = await crud.get_product_by_atomy_id(
        session=session,
        atomy_id=atomy_id,
        warehouse_id=warehouse_id
    )

    if product is None:
        raise exc404


async def update_product(
        session: AsyncSession,
        atomy_id: str,
        employee_id: int,
        warehouse_id: int,
        schema: ProductUpdateSchema
):
    await check_user_in_employees(
        session=session,
        employee_id=employee_id,
        warehouse_id=warehouse_id
    )

    product = await crud.get_product_by_atomy_id(
        session=session,
        atomy_id=atomy_id,
        warehouse_id=warehouse_id
    )

    if product is None:
        raise exc404

    product = await crud.update_product(
        session=session,
        product=product,
        product_update=schema
    )

    return product


