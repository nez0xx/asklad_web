from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import func
from src.core.database import Product, Order, UnitedOrder
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.db_model_order_product_association import ProductOrderAssociation
from .schemas import ProductBase, ProductUpdateSchema


async def create_product(session: AsyncSession, product_schema: ProductBase, warehouse_id: int):

    stmt = (
        select(Product)
        .where(Product.id == product_schema.atomy_id)
    )
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if product is None:
        product = Product(title=product_schema.title, id=product_schema.atomy_id)
        session.add(product)

    await session.commit()
    return product


async def get_products_in_warehouse(session: AsyncSession, warehouse_id: int):

    stmt = (select(ProductOrderAssociation, func.sum(ProductOrderAssociation.amount))
            .options(
        joinedload(ProductOrderAssociation.order),
        joinedload(ProductOrderAssociation.product),
    )
            .join(Order)
            .join(UnitedOrder, Order.united_order_id == UnitedOrder.id)
            .where(Order.warehouse_id == warehouse_id)
            .where(Order.is_given_out == False)
            .where(UnitedOrder.delivered == True)
            .group_by(ProductOrderAssociation.product_id))

    result = await session.execute(stmt)
    products = result.all()
    print(products)
    return products


async def get_product_by_id(session: AsyncSession, product_id: int):

    stmt = (
        select(Product)
        .options(selectinload(Product.orders_details))
        .where(Product.id == product_id)
    )

    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    return product


async def change_product_amount(session: AsyncSession, association: ProductOrderAssociation, amount: int):

    association.amount = amount

    if amount == 0:
        stmt = delete(ProductOrderAssociation).where(ProductOrderAssociation.id == association.id)
        await session.execute(stmt)

    await session.commit()


async def get_product_order_association(
        session: AsyncSession,
        order_id: str,
        product_id: str
) -> ProductOrderAssociation | None:

    stmt = (select(ProductOrderAssociation)
            .where(ProductOrderAssociation.order_id == order_id)
            .where(ProductOrderAssociation.product_id == product_id))

    result = await session.execute(stmt)
    association = result.scalar_one_or_none()

    return association


async def get_product_by_atomy_id(session: AsyncSession, atomy_id: str):

    stmt = (
        select(Product)
        .options(selectinload(Product.orders_details))
        .where(Product.id == atomy_id)
    )

    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    return product





