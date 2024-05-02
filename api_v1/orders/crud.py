from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.database import Order, Product
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import OrderCreate
from .products.crud import create_product


async def create_order(session: AsyncSession, order_schema: OrderCreate, owner_id: int):

    order = Order(
        customer=order_schema.customer,
        customer_phone=order_schema.customer_phone,
        owner=owner_id
    )

    for product_schema in order_schema.products:

        product = await create_product(
            session=session,
            product_schema=product_schema,
            owner_id=owner_id
        )
        order.products.append(product)

    session.add(order)
    await session.commit()
    return order



