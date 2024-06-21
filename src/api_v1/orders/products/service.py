from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.orders.products import crud
from src.api_v1.orders.products.schemas import ProductUpdateSchema, ProductInWarehouseSchema
from src.api_v1.warehouses.utils import check_user_in_employees


exc404 = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"Product with this id does not exist in the warehouse"
)


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

    results = await crud.get_products_in_warehouse(session, warehouse_id)
    products = []

    for elem in results:
        products.append(ProductInWarehouseSchema(title=elem[0].product.title, amount=elem[1]))

    return products


async def change_product_amount(
        session: AsyncSession,
        order_id: str,
        product_id: str,
        amount: int
):
    if amount < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Amount has be >= 0"
        )

    association = await crud.get_product_order_association(
        session=session,
        order_id=order_id,
        product_id=product_id
    )

    if association is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ProductAssociation order_id={order_id} product_id={product_id} does not exist"
        )

    await crud.change_product_amount(
        session=session,
        association=association,
        amount=amount
    )



