from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from .schemas import CustomerBaseSchema
from src.core.database import Customer, Order
from sqlalchemy.ext.asyncio import AsyncSession


async def get_warehouse_customers(session: AsyncSession, warehouse_id: int):
    stmt = (
        select(Customer, func.count(Customer.id))
        .outerjoin(Order, Customer.id == Order.customer_id)
        .group_by(Customer.atomy_id)
        .where(Customer.warehouse_id == warehouse_id))

    result = await session.execute(stmt)

    customers = result.all()
    return customers


async def get_or_create_customer(session: AsyncSession, customer_schema: CustomerBaseSchema, warehouse_id: int):

    stmt = (
        select(Customer)
        .where(Customer.id == customer_schema.atomy_id)
    )

    result = await session.execute(stmt)
    customer = result.scalar_one_or_none()

    if customer is None:
        customer = Customer(name=customer_schema.name, id=customer_schema.atomy_id)
        session.add(customer)
        await session.commit()

    return customer


async def get_customer_or_none(session: AsyncSession, customer_atomy_id: str, warehouse_id: int):
    stmt = (
        select(Customer).options(selectinload(Customer.orders))
        .where(Customer.atomy_id == customer_atomy_id)
        .where(Customer.warehouse_id == warehouse_id)
    )
    result = await session.execute(stmt)
    customer = result.scalar_one_or_none()

    return customer
