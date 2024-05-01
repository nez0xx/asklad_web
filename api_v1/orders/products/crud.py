from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.database import Product
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import Product


async def create_product(session: AsyncSession, product_in: Product, owner_id: int):

    product = Product(**product_in.model_dump(), owner=owner_id)
    session.add(product)
    await session.commit()
    return product
