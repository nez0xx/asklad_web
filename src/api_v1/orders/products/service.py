from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.orders.products import crud
from src.api_v1.orders.products.schemas import ProductUpdateSchema, ProductInWarehouseSchema
from src.api_v1.warehouses.utils import check_user_in_employees


exc404 = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"Product with this id does not exist in the warehouse"
)

'''
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
'''

async def products_list(
        session: AsyncSession,
        warehouse_id: int,
        employee_id: int
):
    await check_user_in_employees(
        session=session,
        warehouse_id=warehouse_id,
        employee_id=employee_id
    )
    print(employee_id)
    results = await crud.get_all_products(session, warehouse_id)
    products = []

    for elem in results:
        products.append(ProductInWarehouseSchema(title=elem[0].product.title, amount=elem[1]))
    print(products)
    return products


