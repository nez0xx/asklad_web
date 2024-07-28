from datetime import date, timezone, timedelta

from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload, joinedload

from src.core.database import Order, UnitedOrder, Product, ProductOrderAssociation
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import OrderSchema
from .products.crud import create_product, get_product_by_id
from .utils import normalize_phone


async def create_united_order(
        session: AsyncSession,
        united_order_id: str,
        warehouse_id: int
) -> UnitedOrder:

    united_order = UnitedOrder(id=united_order_id, warehouse_id=warehouse_id)
    session.add(united_order)
    await session.commit()
    return united_order


async def get_united_order_by_id(session: AsyncSession, united_order_id: str) -> UnitedOrder | None:
    stmt = (
        select(UnitedOrder)
        .options(selectinload(UnitedOrder.orders_relationship), selectinload(UnitedOrder.employee_relationship))
        .where(UnitedOrder.id == united_order_id)
    )
    result = await session.execute(stmt)
    united_order = result.scalar_one_or_none()

    return united_order


async def get_order_by_id(session: AsyncSession, order_id: str) -> Order | None:

    stmt = (
        select(Order)
        .options(selectinload(Order.products_details), selectinload(Order.given_by_relationship))
        .where(Order.id == order_id)
    )

    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    return order


async def create_order(
        session: AsyncSession,
        customer_id: int,
        united_order_id: str,
        order_schema: OrderSchema,
        warehouse_id: int
) -> str:

    phone = normalize_phone(order_schema.customer_phone)

    order = Order(
        id=order_schema.order_id,
        customer_id=customer_id,
        customer_name=order_schema.customer_name,
        customer_phone=phone,
        warehouse_id=warehouse_id,
        united_order_id=united_order_id
    )
    session.add(order)

    for product_schema in order_schema.products:

        product = await create_product(
            session=session,
            product_schema=product_schema
        )
        session.add(ProductOrderAssociation(
            product_id=product.id,
            amount=product_schema.amount,
            order_id=order.id
        ))

    await session.commit()
    return order.id


async def get_united_orders(session: AsyncSession, warehouse_id: int) -> list[UnitedOrder]:
    stmt = (select(UnitedOrder)
            .options(selectinload(UnitedOrder.employee_relationship))
            .where(UnitedOrder.warehouse_id == warehouse_id)
            .order_by(UnitedOrder.created_at))

    result = await session.execute(stmt)
    orders = list(result.scalars())

    return orders


async def get_all_orders(
        session: AsyncSession,
        warehouse_id: int,
        is_given_out: bool | None = None,
        search_id: str | None = None,
        search_name: str | None = None
) -> list[Order] | None:

    stmt = (
        select(Order)
        .options(selectinload(Order.products_details), selectinload(Order.customer_relationship))
        .where(Order.warehouse_id == warehouse_id)
    )
    if search_id:
        stmt = stmt.where(Order.id.contains(search_id))
    if search_name:
        stmt = stmt.where(Order.customer_name.contains(search_name))
    if is_given_out is not None:
        stmt = stmt.where(Order.is_given_out == is_given_out)

    result = await session.execute(stmt)
    scalars_result = result.scalars().all()
    return [order for order in scalars_result]


async def give_order_out(
        session: AsyncSession,
        order_id: str,
        given_by: int,
        comment: str | None
) -> Order | None:

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
        order.issue_date = date.today()
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
        united_order: UnitedOrder,
        employee_id: int
):
    united_order.delivered = True
    united_order.accepted_by = employee_id
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
    await session.close()


async def get_united_orders_by_date(
        session: AsyncSession,
        warehouse_id: int,
        date_min: date,
        date_max: date
) -> list[UnitedOrder]:
    print(warehouse_id, date_min, date_max)
    stmt = (select(UnitedOrder)
            .options(selectinload(UnitedOrder.orders_relationship))
            .where(UnitedOrder.warehouse_id == warehouse_id)
            .where(UnitedOrder.delivered == True)
            .where(UnitedOrder.delivery_date >= date_min)
            .where(UnitedOrder.delivery_date <= date_max)
    )
    result = await session.execute(stmt)
    united_orders = list(result.scalars())
    return united_orders


async def get_order_cost(
        session: AsyncSession,
        order_id: str
) -> dict:
    order_price = 0
    order_pv = 0

    order = await get_order_by_id(
        session=session,
        order_id=order_id
    )

    for association in order.products_details:
        product = await get_product_by_id(
            session=session,
            product_id=association.product_id
        )
        order_price += product.price * association.amount
        order_pv += product.pv * association.amount

    return {
        "order_price": order_price,
        "order_pv": order_pv
    }


async def get_united_order_price(
        session: AsyncSession,
        united_order: UnitedOrder
) -> dict[str: int]:
    united_order_price = 0
    united_order_pv = 0

    for order in united_order.orders_relationship:
        data = await get_order_cost(session=session, order_id=order.id)
        united_order_price += data["order_price"]
        united_order_pv += data["order_pv"]

    return {
        "united_order_price": united_order_price,
        "united_order_pv": united_order_pv
    }
