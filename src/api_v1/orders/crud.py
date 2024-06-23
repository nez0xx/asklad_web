from datetime import date

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from src.core.database import Order, UnitedOrder
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import ProductOrderAssociation
from .schemas import OrderBase
from .products.crud import create_product, get_product_by_id


async def create_united_order(session: AsyncSession, united_order_id: str, warehouse_id: int):

    order = UnitedOrder(id=united_order_id, warehouse_id=warehouse_id)
    session.add(order)
    await session.commit()
    return order


async def get_united_order_by_id(session: AsyncSession, united_order_id: str):
    stmt = (
        select(UnitedOrder)
        .options(selectinload(UnitedOrder.orders_relationship))
        .where(UnitedOrder.id == united_order_id)
    )
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    return order


async def get_order_by_id(session: AsyncSession, order_id: str) -> Order | None:

    stmt = (
        select(Order)
        .options(selectinload(Order.products_details))
        .where(Order.id == order_id)
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


async def get_united_orders(session: AsyncSession, warehouse_id: int):
    stmt = (select(UnitedOrder)
            .where(UnitedOrder.warehouse_id == warehouse_id))
    result = await session.execute(stmt)
    orders = result.scalars().all()
    return orders


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
    return [order for order in scalars_result]


async def give_out(session: AsyncSession, order_id: str, given_by: int, comment: str | None) -> Order | None:

    stmt = (
        select(Order)
        .options(selectinload(Order.products_details))
        .where(Order.id == order_id)
    )

    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if order:

        for assoc in order.products_details:
            product = await get_product_by_id(
                session=session,
                product_id=assoc.product_id
                )
        order.comment = comment
        order.is_given_out = True
        order.given_by = given_by  # кем выдан
        await session.commit()

    return order


async def get_orders_in_united_order(
        session: AsyncSession,
        united_order_id: str
) -> list[Order]:

    stmt = select(Order).options(selectinload(Order.products_details)).where(Order.united_order_id == united_order_id)
    result = await session.execute(stmt)
    orders = list(result.scalars())

    return orders


async def delivery_united_order(
        session: AsyncSession,
        united_order: UnitedOrder
):
    united_order.delivered = True
    united_order.delivery_date = date.today()
    await session.commit()


async def delete_united_order(
        session: AsyncSession,
        united_order_id: str
):

    stmt_get_products = select(ProductOrderAssociation.id).join(Order).where(Order.united_order_id == united_order_id)
    result = await session.execute(stmt_get_products)
    ids = [elem[0] for elem in result.all()]

    stmt_delete_products = delete(ProductOrderAssociation).where(ProductOrderAssociation.id.in_(ids))
    stmt_delete_orders = delete(Order).where(Order.united_order_id == united_order_id)
    stmt_delete_united_order = delete(UnitedOrder).where(UnitedOrder.id == united_order_id)

    await session.execute(stmt_delete_products)
    await session.execute(stmt_delete_orders)
    await session.execute(stmt_delete_united_order)
    await session.commit()


