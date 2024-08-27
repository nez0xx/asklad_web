import os
from datetime import date, datetime
from typing import Sequence

import requests
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.orders import crud, utils
from src.api_v1.orders.crud import get_order_by_id, create_order, create_united_order, get_united_order_by_id
from src.api_v1.orders.customers.crud import get_or_create_customer
from src.api_v1.orders.products.crud import get_product_by_id
from src.api_v1.orders.schemas import UnitedOrderSchema, OrderSchema, OrderTgSchema, ProductTgSchema
from src.api_v1.orders.utils import parse_excel, create_payment_list_excel

from src.api_v1.warehouses.crud import get_user_own_warehouse, get_warehouse_by_id, get_user_available_warehouse
from src.api_v1.warehouses.utils import check_user_in_employees

from src.core.database import Warehouse, User, Order, UnitedOrder
from src.core.settings import BASE_DIR, settings

from src.pdf_parser import convert_pdf
from .exceptions import OrderExists, UnitedOrderExists, WarehouseNotFound, UnitedOrderNotFound, OrderNotFound, \
    OrderIsGivenOut, NotDelivered, AlreadyDelivered

from .products.schemas import ProductSchema

from .utils import normalize_phone


NOTIFICATION_BOT_URL = settings.NOTIFICATION_BOT_URL


async def add_united_order_service(
        session: AsyncSession,
        united_order_schema: UnitedOrderSchema,
        employee_id: int
) -> list[str]:

    await check_user_in_employees(
        session=session,
        employee_id=employee_id,
        warehouse_id=united_order_schema.warehouse_id
    )

    united_order = await get_united_order_by_id(session=session, united_order_id=united_order_schema.united_order_id)

    if united_order:
        raise UnitedOrderExists()

    for order_schema in united_order_schema.orders:

        order = await get_order_by_id(
            session=session,
            order_id=order_schema.order_id
        )

        if order:
            raise OrderExists()

    await create_united_order(
        session,
        united_order_schema.united_order_id,
        warehouse_id=united_order_schema.warehouse_id
    )

    customers = []

    for order_schema in united_order_schema.orders:

        customer = await get_or_create_customer(
            session=session,
            customer_name=order_schema.customer_name,
            customer_id=order_schema.customer_id
        )

        await create_order(
            session,
            customer_id=customer.id,
            order_schema=order_schema,
            united_order_id=united_order_schema.united_order_id,
            warehouse_id=united_order_schema.warehouse_id
        )
        customers.append(order_schema.customer_name)
    await session.commit()

    return customers


async def get_order_service(
        session: AsyncSession,
        employee_id: int,
        order_id: str
) -> OrderSchema | None:
    order = await crud.get_order_by_id(
        session=session,
        order_id=order_id
    )

    if order is None:
        return None

    await check_user_in_employees(
        session=session,
        employee_id=employee_id,
        warehouse_id=order.warehouse_id
    )

    order_schema = OrderSchema(
        order_id=order.id,
        customer_name=order.customer_name,
        customer_id=order.customer_id,
        customer_phone=order.customer_phone,
        comment=order.comment,
        products=[]
    )

    if order.given_by_relationship != None:
        order_schema.given_by = order.given_by_relationship.name

    for association in order.products_details:
        product = await get_product_by_id(
            session=session,
            product_id=association.product_id
        )
        product_schema = ProductSchema(
            title=product.title,
            product_id=product.id,
            amount=association.amount
        )
        order_schema.products.append(product_schema)

    return order_schema


async def get_all_orders_service(
        session: AsyncSession,
        employee_id: int,
        is_given_out: bool | None,
        search_id: str | None = None,
        search_name: str | None = None
) -> list[Order]:
    warehouse = await get_user_available_warehouse(session, employee_id)

    if warehouse is None:
        raise WarehouseNotFound()

    orders = await crud.get_all_orders(
            session=session,
            warehouse_id=warehouse.id,
            is_given_out=is_given_out,
            search_id=search_id,
            search_name=search_name
        )

    return orders


async def get_united_order_service(
        session: AsyncSession,
        united_order_id: str,
        employee_id: int
) -> UnitedOrder:
    order = await get_united_order_by_id(session, united_order_id)
    if order is None:
        raise UnitedOrderNotFound()

    await check_user_in_employees(session, employee_id, order.warehouse_id)
    return order


async def get_united_orders(
        session: AsyncSession,
        warehouse_id: int
) -> Sequence[UnitedOrder]:
    orders = await crud.get_united_orders(
        session=session,
        warehouse_id=warehouse_id
    )
    return orders


async def give_order_out_service(
        session: AsyncSession,
        order_id: str,
        employee_id: int,
        comment: str | None
) -> Order:
    order = await crud.get_order_by_id(
        session=session,
        order_id=order_id
    )
    if order is None:
        raise OrderNotFound()

    if order.is_given_out:
        raise OrderIsGivenOut()

    united_order = await get_united_order_by_id(
        session=session,
        united_order_id=order.united_order_id
    )

    if not united_order.delivered:
        raise NotDelivered()

    warehouse_id = order.warehouse_id

    await check_user_in_employees(
        session=session,
        warehouse_id=warehouse_id,
        employee_id=employee_id
    )

    order = await crud.give_order_out(
        session=session,
        order_id=order_id,
        given_by=employee_id,
        comment=comment
    )

    if order is None:
        raise OrderNotFound()

    return order


async def add_orders_from_file(
        session: AsyncSession,
        file: UploadFile,
        employee_id: int,
        warehouse_id: int
) -> list[str]:

    united_orders = await parse_excel(file)
    united_orders_ids = []
    customers = []

    # проверка на возможное отстутствие заказов в бд
    for united_order in united_orders:
        united_order_id = united_order["united_order_id"]
        united_order = await crud.get_united_order_by_id(session, united_order_id)

        if united_order:
            raise OrderExists()

    for united_order in united_orders:
        united_order["warehouse_id"] = warehouse_id
        schema = UnitedOrderSchema(**united_order)
        order_customers = await add_united_order_service(session, schema, employee_id=employee_id)
        customers.extend(order_customers)

    return customers


async def notify_customers(
        session: AsyncSession,
        united_order_id: str,
        warehouse_name: str
) -> int:
    orders = await crud.get_orders_in_united_order(
        session=session,
        united_order_id=united_order_id
    )

    data = []

    for order in orders:
        order_info = OrderTgSchema(
            customer_phone=normalize_phone(order.customer_phone),
            warehouse_name=warehouse_name,
            order_id=order.id,
            products_list=[]
        )
        for assoc in order.products_details:
            product = await get_product_by_id(
                session=session,
                product_id=assoc.product_id
            )

            order_info.products_list.append(
                ProductTgSchema(
                    title=product.title,
                    amount=assoc.amount
                )
            )
        data.append(order_info.model_dump())

    request = requests.post(url=NOTIFICATION_BOT_URL, json=data)

    return request.status_code


async def delivery_united_order_service(
        session: AsyncSession,
        united_order_id: str,
        notificate: bool,
        user: User
):

    united_order = await crud.get_united_order_by_id(
        session=session,
        united_order_id=united_order_id
    )
    if united_order is None:
        raise UnitedOrderNotFound()
    # если заказ уже доставлен и юзеров уведомили, кидаем ошибку
    if united_order.delivered:
        raise AlreadyDelivered()

    warehouse = await get_warehouse_by_id(
        session=session,
        warehouse_id=united_order.warehouse_id
    )

    await check_user_in_employees(
        session=session,
        employee_id=user.id,
        warehouse_id=warehouse.id
    )

    await crud.delivery_united_order(
        session=session,
        united_order=united_order,
        employee_id=user.id
    )


async def delete_united_order(
        session: AsyncSession,
        united_order_id: str
):
    united_order = await crud.get_united_order_by_id(
        session=session,
        united_order_id=united_order_id
    )

    if united_order is None:
        raise OrderNotFound()

    await crud.delete_united_order(
        session=session,
        united_order_id=united_order_id
    )


async def create_issue_list(
        session: AsyncSession,
        united_order_ids: list[str],
        warehouse: Warehouse
) -> str:
    united_orders = []
    for united_order_id in united_order_ids:

        united_order = await get_united_order_by_id(session=session, united_order_id=united_order_id)

        if united_order is None:
            raise UnitedOrderNotFound()
        if united_order.warehouse_id != warehouse.id:
            raise UnitedOrderNotFound()

        united_orders.append(united_order)
    filename = await create_payment_list_excel(united_orders)
    return filename


async def get_total_united_orders_cost(
        session: AsyncSession,
        warehouse: Warehouse,
        date_min: date,
        date_max: date = date.today()
) -> dict:
    data = {
        "total_price": {},
        "total_pv": 0,
        "orders": {}
    }
    total_price = 0
    total_pv = 0

    united_orders = await crud.get_united_orders_by_date(
        session=session,
        warehouse_id=warehouse.id,
        date_min=date_min,
        date_max=date_max
    )
    print("dadadad")
    print(united_orders)
    for united_order in united_orders:
        united_order_data = await crud.get_united_order_price(
            session=session,
            united_order=united_order
        )
        print(data, "data")
        total_price += united_order_data["united_order_price"]
        total_pv += united_order_data["united_order_pv"]

        data["orders"][united_order.id] = {}
        data["orders"][united_order.id]["rub"] = united_order_data["united_order_price"]
        data["orders"][united_order.id]["pv"] = united_order_data["united_order_pv"]

    data["total_price"]["rub"] = total_price
    data["total_pv"] = total_pv

    return data


async def parse_pdf_service(file: UploadFile):
    filename = await utils.save_file(file)
    converted_file = convert_pdf(filename)
    os.remove(filename)

    return converted_file




















