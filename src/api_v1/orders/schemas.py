from pydantic import BaseModel

from .customers.schemas import CustomerBaseSchema
from .products.schemas import ProductSchema


class OrderSchema(BaseModel):

    order_id: str

    customer_phone: str

    customer_name: str

    customer_id: str

    given_by: str | None = None

    comment: str | None = None

    products: list[ProductSchema]


class UnitedOrderSchema(BaseModel):
    warehouse_id: int
    united_order_id: str
    orders: list[OrderSchema]


class OrderListItem(BaseModel):

    customer_phone: str

# ДЛЯ ОТПРАВКИ АПИ ТГ БОТА
class ProductTgSchema(BaseModel):
    title: str
    amount: int


class OrderTgSchema(BaseModel):
    customer_phone: str
    order_id: str
    warehouse_name: str
    products_list: list[ProductTgSchema]










