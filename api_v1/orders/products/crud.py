from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.database import Product
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import ProductCreate


async def create_product(session: AsyncSession, product_schema: ProductCreate, owner_id: int):

    stmt = (
        select(Product)
        .where(Product.id == product_schema.id)
        .where(Product.owner == owner_id)
    )
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if product is None:
        product = Product(**product_schema.model_dump(), owner=owner_id)
        session.add(product)

    else:
        product.amount += product_schema.amount

    await session.commit()
    return product

async def get_all_products(session: AsyncSession, owner_id):

    stmt = select(Product).where(Product.owner == owner_id)
    result = await session.execute(stmt)
    products = result.scalars().all()
    return products


