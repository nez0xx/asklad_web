from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from .schemas import CustomeBaseSchema
from src.core.database import Customer, Order
from sqlalchemy.ext.asyncio import AsyncSession


async def get_all_customers(session: AsyncSession, owner_id: int):
    stmt = (
        select(Customer, func.count(Customer.id))
        .outerjoin(Order, Customer.id == Order.customer_id)
        .group_by(Customer.atomy_id)
        .where(Customer.owner == owner_id))

    result = await session.execute(stmt)

    customers = result.all()
    return customers


async def get_or_create_customer(session: AsyncSession, customer_schema: CustomeBaseSchema, owner_id: int):

    stmt = (
        select(Customer)
        .where(Customer.atomy_id == customer_schema.atomy_id)
        .where(Customer.owner == owner_id)
    )

    result = await session.execute(stmt)
    customer = result.scalar_one_or_none()

    if customer is None:
        customer = Customer(**customer_schema.model_dump(), owner=owner_id)
        session.add(customer)
        await session.commit()

    return customer


async def get_customer_or_none(session: AsyncSession, customer_atomy_id: str, owner_id: int):
    stmt = (
        select(Customer).options(selectinload(Customer.orders))
        .where(Customer.atomy_id == customer_atomy_id)
        .where(Customer.owner == owner_id)
    )
    result = await session.execute(stmt)
    customer = result.scalar_one_or_none()

    return customer
