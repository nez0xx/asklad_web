import os
from datetime import datetime

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.orders import crud, utils
from src.api_v1.orders.crud import get_order_by_id, create_order, create_united_order, get_united_order
from src.api_v1.orders.customers.crud import get_or_create_customer
from src.api_v1.orders.schemas import OrderBase, UnitedOrderSchema
from src.api_v1.warehouses.crud import get_user_warehouses
from src.api_v1.warehouses.utils import check_user_in_employees
from src.core.settings import BASE_DIR
from src.parser import parse_excel


async def add_orders(session: AsyncSession, united_order_schema: UnitedOrderSchema, employee_id: int):

    await check_user_in_employees(
        session=session,
        employee_id=employee_id,
        warehouse_id=united_order_schema.warehouse_id
    )

    united_order = await get_united_order(session=session, united_order_id=united_order_schema.united_order_id)
    print("7"*100)
    if united_order:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"United order with id {united_order_schema.united_order_id} already exists"
            )

    for order_schema in united_order_schema.orders:

        order = await get_order_by_id(
            session=session,
            order_id=order_schema.atomy_id
        )

        if order:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Order with id {order_schema.atomy_id} already exists"
            )

        customer = await get_or_create_customer(
            session=session,
            customer_schema=order_schema.customer,
            warehouse_id=united_order_schema.warehouse_id
        )

        await create_order(
            session,
            customer_id=customer.id,
            order_schema=order_schema,
            united_order_id=united_order_schema.united_order_id,
            warehouse_id=united_order_schema.warehouse_id
        )

    await create_united_order(session, united_order_schema.united_order_id, warehouse_id=united_order_schema.warehouse_id)

    return united_order_schema.united_order_id


async def order_info(
        session: AsyncSession,
        employee_id: int,
        order_id: str
):
    order = await crud.get_order_by_id(
        session=session,
        order_id=order_id
    )

    await check_user_in_employees(
        session=session,
        employee_id=employee_id,
        warehouse_id=order.warehouse_id
    )

    return order


async def all_orders_info(
        session: AsyncSession,
        employee_id: int,
        is_given_out: bool | None
):
    '''
    await check_user_in_employees(
        session=session,
        employee_id=employee_id,
        warehouse_id=warehouse_id
    )
    '''
    warehouses = await get_user_warehouses(session, employee_id)
    orders_list = []
    for warehouse in warehouses:
        orders = await crud.get_all_orders(
            session=session,
            warehouse_id=warehouse.id,
            is_given_out=is_given_out
        )
        orders_list.extend(orders)

    return orders_list


async def get_orders_in_warehouse(
        session: AsyncSession,
        warehouse_id: int,
        employee_id: int,
        is_given_out: bool = None
):
    await check_user_in_employees(session=session, warehouse_id=warehouse_id, employee_id=employee_id)
    orders = await crud.get_all_orders(
        session=session,
        warehouse_id=warehouse_id,
        is_given_out=is_given_out
    )
    return orders


async def united_order_info(session: AsyncSession, order_id: str, employee_id: int):
    order = await get_united_order(session, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"United order with id {order_id} does not exist"
        )
    
    await check_user_in_employees(session, employee_id, order.warehouse_id)
    return order


async def get_united_orders(session: AsyncSession, warehouse_id: int, employee_id: int):
    await check_user_in_employees(session=session, warehouse_id=warehouse_id, employee_id=employee_id)

    orders = await crud.get_united_orders(session=session, warehouse_id=warehouse_id)
    return orders


async def give_order_out(session: AsyncSession, order_id: str, employee_id: int):
    order = await crud.get_order_by_id(session=session, order_id=order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} does not exist"
        )

    warehouse_id = order.warehouse_id
    await check_user_in_employees(session=session, warehouse_id=warehouse_id, employee_id=employee_id)
    order = await crud.give_out(session=session, order_id=order_id, given_by=employee_id)
    return order


async def add_orders_from_file(session: AsyncSession, file: UploadFile, employee_id: int, warehouse_id: int):
    content = await file.read()
    date = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    filename = f"{date}_{file.filename}"
    full_filename = os.path.join(BASE_DIR, 'uploaded_files', filename)

    with open(full_filename, "wb") as f:
        f.write(content)

    data = parse_excel(full_filename)
    data["warehouse_id"] = warehouse_id
    schema = UnitedOrderSchema(**data)
    order_id = await add_orders(session, schema, employee_id=employee_id)
    return order_id

























