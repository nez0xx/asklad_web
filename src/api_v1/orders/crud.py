from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.database import Order, UnitedOrder
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.db_model_order_product_association import ProductOrderAssociation
from .customers.crud import get_or_create_customer
from .schemas import OrderBase
from .products.crud import create_product, get_product_by_id


async def create_united_order(session: AsyncSession, united_order_id: str):

    order = UnitedOrder(id=united_order_id)
    session.add(order)
    await session.commit()
    return order


async def get_order_by_id(session: AsyncSession, id: str, warehouse_id: int) -> Order | None:

    stmt = (
        select(Order)
        .options(selectinload(Order.products_details))
        .where(Order.id == id)
        .where(Order.warehouse_id == warehouse_id)
    )

    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    return order


async def create_order(
        session: AsyncSession,
        customer_id: int,
        united_order_id: str,
        order_schema: OrderBase,
        warehouse_id: int
):

    order = Order(
        id=order_schema.atomy_id,
        customer_id=customer_id,
        customer_phone=order_schema.customer_phone,
        warehouse_id=warehouse_id,
        united_order_id=united_order_id
    )

    for product_schema in order_schema.products:

        product = await create_product(
            session=session,
            product_schema=product_schema,
            warehouse_id=warehouse_id
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
        warehouse_id: int,
        is_given_out: bool | None = None
) -> list[Order] | None:

    stmt = (
        select(Order)
        .options(selectinload(Order.products_details), selectinload(Order.customer_relationship))
        .where(Order.warehouse_id == warehouse_id)
    )

    if is_given_out is not None:
        stmt = stmt.where(Order.is_given_out == is_given_out)

    result = await session.execute(stmt)
    scalars_result = result.scalars().all()
    return [product for product in scalars_result]


async def give_out(session: AsyncSession, order_id: str, warehouse_id: int):

    stmt = (
        select(Order)
        .options(selectinload(Order.products_details))
        .where(Order.id == order_id)
        .where(Order.warehouse_id == warehouse_id)
    )

    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if order:

        for assoc in order.products_details:
            product = await get_product_by_id(
                session=session,
                product_id=assoc.product_id,
                warehouse_id=warehouse_id
                )
            product.amount -= assoc.amount

        order.is_given_out = True
        await session.commit()

    return order

