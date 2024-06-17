from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import func
from src.core.database import Product, Order
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


async def get_all_products(session: AsyncSession, warehouse_id: int):

    stmt = (select(ProductOrderAssociation, func.sum(ProductOrderAssociation.amount))
            .options(joinedload(ProductOrderAssociation.order), joinedload(ProductOrderAssociation.product))
            .join(Order)
            .where(Order.warehouse_id == warehouse_id)
            .group_by(ProductOrderAssociation.product_id))
    result = await session.execute(stmt)
    #print(result.scalars(), result.all())

    products = result.all()

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


async def get_product_by_atomy_id(session: AsyncSession, atomy_id: str):

    stmt = (
        select(Product)
        .options(selectinload(Product.orders_details))
        .where(Product.id == atomy_id)
    )

    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    return product


async def update_product(
    session: AsyncSession,
    product: Product,
    product_update: ProductUpdateSchema
) -> Product:
    for name, value in product_update.model_dump(exclude_unset=True).items():
        setattr(product, name, value)
    await session.commit()
    return product



