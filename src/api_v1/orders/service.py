from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.orders import crud, utils
from src.api_v1.orders.crud import get_order_by_id, create_order, create_united_order, get_united_order_by_id
from src.api_v1.orders.customers.crud import get_or_create_customer
from src.api_v1.orders.products.crud import get_product_by_id
from src.api_v1.orders.schemas import UnitedOrderSchema, OrderSchema
from src.api_v1.orders.utils import parse_excel, create_payment_list_excel
from src.api_v1.warehouses.crud import get_user_own_warehouse, get_warehouse_by_id, get_user_available_warehouse
from src.api_v1.warehouses.utils import check_user_in_employees
from src.core.database import Warehouse
from src.core.settings import BASE_DIR
from src.parser import parse
from .products.schemas import ProductSchema
from .utils import normalize_phone


async def add_united_order(session: AsyncSession, united_order_schema: UnitedOrderSchema, employee_id: int):

    await check_user_in_employees(
        session=session,
        employee_id=employee_id,
        warehouse_id=united_order_schema.warehouse_id
    )

    united_order = await get_united_order_by_id(session=session, united_order_id=united_order_schema.united_order_id)

    if united_order:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"United order with id {united_order_schema.united_order_id} already exists"
            )

    for order_schema in united_order_schema.orders:

        order = await get_order_by_id(
            session=session,
            order_id=order_schema.order_id
        )

        if order:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Order with id {order_schema.atomy_id} already exists"
            )

    await create_united_order(
        session,
        united_order_schema.united_order_id,
        warehouse_id=united_order_schema.warehouse_id
    )

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

    return united_order_schema.united_order_id


async def get_order(
        session: AsyncSession,
        employee_id: int,
        order_id: str
):
    print("1"*100)
    order = await crud.get_order_by_id(
        session=session,
        order_id=order_id
    )
    print("ВСЕ НОРМ"*100)
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
        products=[]
    )

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


async def get_all_orders(
        session: AsyncSession,
        employee_id: int,
        is_given_out: bool | None
):
    warehouse = await get_user_available_warehouse(session, employee_id)

    if warehouse is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You dont manage any warehouse"
        )
    orders = await crud.get_all_orders(
            session=session,
            warehouse_id=warehouse.id,
            is_given_out=is_given_out
        )

    return orders


async def get_orders_in_warehouse(
        session: AsyncSession,
        warehouse_id: int,
        employee_id: int,
        is_given_out: bool = None
):
    orders = await crud.get_all_orders(
        session=session,
        warehouse_id=warehouse_id,
        is_given_out=is_given_out
    )
    return orders


async def united_order_info(session: AsyncSession, order_id: str, employee_id: int):
    order = await get_united_order_by_id(session, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"United order with id {order_id} does not exist"
        )
    
    await check_user_in_employees(session, employee_id, order.warehouse_id)
    return order


async def get_united_orders(session: AsyncSession, warehouse_id: int):
    orders = await crud.get_united_orders(
        session=session,
        warehouse_id=warehouse_id
    )
    return orders


async def give_order_out(session: AsyncSession, order_id: str, employee_id: int, comment: str | None):
    order = await crud.get_order_by_id(
        session=session,
        order_id=order_id
    )
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} does not exist"
        )

    united_order = await get_united_order_by_id(
        session=session,
        united_order_id=order.united_order_id
    )

    if not united_order.delivered:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"United order with id {united_order.id} has not been delivered"
        )
    warehouse_id = order.warehouse_id

    await check_user_in_employees(
        session=session,
        warehouse_id=warehouse_id,
        employee_id=employee_id
    )

    order = await crud.give_out(
        session=session,
        order_id=order_id,
        given_by=employee_id,
        comment=comment
    )

    return order


async def add_orders_from_file(session: AsyncSession, file: UploadFile, employee_id: int, warehouse_id: int):

    united_orders = await parse_excel(file)
    united_orders_ids = []

    # проверка на отстутствие заказов в бд
    for united_order in united_orders:
        united_order_id = united_order["united_order_id"]
        united_order = await crud.get_united_order_by_id(session, united_order_id)

        if united_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {united_order_id} already exists"
            )

    for united_order in united_orders:
        print(united_order)
        united_order["warehouse_id"] = warehouse_id
        schema = UnitedOrderSchema(**united_order)
        united_order_id = await add_united_order(session, schema, employee_id=employee_id)
        united_orders_ids.append(united_order_id)

    return united_orders_ids


async def notify_customers(
        session: AsyncSession,
        united_order_id: str
) -> int:
    united_order = await crud.get_united_order_by_id(
        session=session,
        united_order_id=united_order_id
    )
    if united_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"United order with id {united_order_id} does not exist"
        )
    # если заказ уже доставлен и юзеров уведомили, кидаем ошибку
    if united_order.delivered:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"Order {united_order.id} already has been delivered"
        )

    warehouse = await get_warehouse_by_id(
        session=session,
        warehouse_id=united_order.warehouse_id
    )

    orders = await crud.get_orders_in_united_order(
        session=session,
        united_order_id=united_order_id
    )

    data = []
    '''
    for order in orders:
        order_info = OrderInfoSchema(
            customer_phone=normalize_phone(order.customer_phone),
            warehouse_name=warehouse.name,
            order_id=order.id,
            products_list=[]
        )
        for assoc in order.products_details:

            product = await get_product_by_id(
                session=session,
                product_id=assoc.product_id
            )

            order_info.products_list.append(
                ProductSchema(
                    title=product.title,
                    amount=assoc.amount
                )
            )
        data.append(order_info.model_dump())

    request = requests.post(url="http://127.0.0.1:9000", json=data)

    if request.status_code == 200:
        await crud.delivery_united_order(
            session=session,
            united_order=united_order
        )

    return request.status_code
    '''
    await crud.delivery_united_order(
        session=session,
        united_order=united_order
    )
    return 1


async def delete_united_order(
        session: AsyncSession,
        united_order_id: str
):
    united_order = await crud.get_united_order_by_id(
        session=session,
        united_order_id=united_order_id
    )

    if united_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="United order does not exist"
        )

    await crud.delete_united_order(
        session=session,
        united_order_id=united_order_id
    )


async def create_issue_list(session: AsyncSession, united_order_id: str, warehouse: Warehouse):
    united_order = await get_united_order_by_id(session=session, united_order_id=united_order_id)
    if united_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"United order {united_order_id} does not exist"
        )
    if united_order.warehouse_id != warehouse.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The united order belongs to another warehouse"
        )
    orders = united_order.orders_relationship
    filename = await create_payment_list_excel(orders)
    return filename

























