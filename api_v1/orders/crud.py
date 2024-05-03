from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.database import Order, Product
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_model_order_product_association import ProductOrderAssociation
from .schemas import OrderCreate
from .products.crud import create_product


async def create_order(session: AsyncSession, order_schema: OrderCreate, owner_id: int):

    order = Order(
        id=order_schema.id,
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
        order.products_details.append(ProductOrderAssociation(
            product=product,
            amount=product_schema.amount
        ))

    session.add(order)
    print("7"*100)
    await session.commit()
    return order


async def get_all_orders(
        session: AsyncSession,
        owner_id: int,
        is_given_out: bool | None = None
) -> list[Order] | None:

    if is_given_out:
        print(is_given_out, type(is_given_out))
        stmt = select(Order).where(Order.owner == owner_id).where(Order.is_given_out == is_given_out)
    else:
        stmt = select(Order).where(Order.owner == owner_id)

    result = await session.execute(stmt)
    scalars_result = result.scalars().all()
    return [product for product in scalars_result]


async def get_order_by_id(session: AsyncSession, id: str) -> Order | None:
    stmt = select(Order).where(Order.id == id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()
    for assoc in order.products_details:
        print(assoc.amount)
    return order


async def give_out(session: AsyncSession, order_id: str, owner_id: int):
    stmt = select(Order).where(Order.id == order_id).where(Order.owner == owner_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()
    if order:
        order.is_given_out = True
        await session.commit()
    return order

