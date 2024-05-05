from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload
from .schemas import CustomerSchema
from core.database import Customer, Order
from sqlalchemy.ext.asyncio import AsyncSession


async def get_all_customers(session: AsyncSession, owner_id: int):

    stmt = (
        select(Order.customer, func.count(Order.customer))
        .join(Order.customer)
        .group_by(Order.customer)
    )

    result = await session.execute(stmt)
    for i in result.fetchall():
        print(i[0], i[1])
    print(result)
    return result


async def get_or_create_customer(session: AsyncSession, customer_schema: CustomerSchema, owner_id: int):

    stmt = (
        select(Customer)
        .where(Customer.id == customer_schema.id)
        .where(Customer.owner == owner_id)
    )
    result = await session.execute(stmt)
    customer = result.scalar_one_or_none()

    if customer is None:
        customer = Customer(**customer_schema.model_dump(), owner=owner_id)
        session.add(customer)
        await session.commit()

    return customer


async def get_customer_or_none(session: AsyncSession, id: str, owner_id: int):
    stmt = (
        select(Customer).options(selectinload(Customer.orders))
        .where(Customer.id == id)
        .where(Customer.owner == owner_id)
    )
    result = await session.execute(stmt)
    customer = result.scalar_one_or_none()

    return customer
