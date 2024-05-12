from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.database import Order
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.db_model_order_product_association import ProductOrderAssociation
from .customers.crud import get_or_create_customer
from .schemas import OrderCreate
from .products.crud import create_product, get_product_by_id


async def get_order_by_id(session: AsyncSession, id: str, owner_id: int) -> Order | None:

    stmt = (
        select(Order)
        .options(selectinload(Order.products_details))
        .where(Order.id == id)
        .where(Order.owner == owner_id)
    )

    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    return order


async def create_order(session: AsyncSession, order_schema: OrderCreate, owner_id: int):

    customer = await get_or_create_customer(
        session=session,
        customer_schema=order_schema.customer,
        owner_id=owner_id
    )

    order = Order(
        id=order_schema.id,
        customer_id=customer.id,
        customer_phone=order_schema.customer_phone,
        owner=owner_id
    )

    for product_schema in order_schema.products:

        product = await create_product(
            session=session,
            product_schema=product_schema,
            owner_id=owner_id
        )
        session.add(ProductOrderAssociation(
            product=product,
            amount=product_schema.amount,
            order=order
        ))

    session.add(order)
    await session.commit()
    return order.id


async def get_all_orders(
        session: AsyncSession,
        owner_id: int,
        is_given_out: bool | None = None
) -> list[Order] | None:

    stmt = (
        select(Order)
        .options(selectinload(Order.products_details), selectinload(Order.customer_relationship))
        .where(Order.owner == owner_id)
    )

    if is_given_out is not None:
        stmt = stmt.where(Order.is_given_out == is_given_out)

    result = await session.execute(stmt)
    scalars_result = result.scalars().all()
    return [product for product in scalars_result]


async def give_out(session: AsyncSession, order_id: str, owner_id: int):

    stmt = (
        select(Order)
        .options(selectinload(Order.products_details))
        .where(Order.id == order_id)
        .where(Order.owner == owner_id)
    )

    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if order:

        for assoc in order.products_details:
            product = await get_product_by_id(
                session=session,
                product_id=assoc.product_id,
                owner_id=owner_id
                )
            product.amount -= assoc.amount

        order.is_given_out = True
        await session.commit()

    return order

