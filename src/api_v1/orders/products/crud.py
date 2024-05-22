from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.database import Product
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import ProductBase, ProductUpdateSchema


async def create_product(session: AsyncSession, product_schema: ProductBase, warehouse_id: int):

    stmt = (
        select(Product)
        .where(Product.atomy_id == product_schema.atomy_id)
        .where(Product.warehouse_id == warehouse_id)
    )
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if product is None:
        product = Product(**product_schema.model_dump(), warehouse_id=warehouse_id)
        session.add(product)

    else:
        product.amount += product_schema.amount

    await session.commit()
    return product


async def get_all_products(session: AsyncSession, warehouse_id: int):

    stmt = select(Product).where(Product.warehouse_id == warehouse_id)
    result = await session.execute(stmt)
    products = result.scalars().all()
    return products


async def get_product_by_id(session: AsyncSession, product_id: int, warehouse_id: int | None = None):

    stmt = (
        select(Product)
        .options(selectinload(Product.orders_details))
        .where(Product.id == product_id)
        .where(Product.warehouse_id == warehouse_id)
    )

    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    return product


async def get_product_by_atomy_id(session: AsyncSession, atomy_id: str, warehouse_id: int | None = None):

    stmt = (
        select(Product)
        .options(selectinload(Product.orders_details))
        .where(Product.atomy_id == atomy_id)
        .where(Product.warehouse_id == warehouse_id)
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



