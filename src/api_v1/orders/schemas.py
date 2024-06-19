from pydantic import BaseModel

from .customers.schemas import CustomerBaseSchema
from .products.schemas import ProductBase


class OrderBase(BaseModel):

    atomy_id: str

    customer_phone: str

    customer: CustomerBaseSchema

    products: list[ProductBase]


class UnitedOrderSchema(BaseModel):
    warehouse_id: int
    united_order_id: str
    orders: list[OrderBase]


class OrderListItem(BaseModel):

    customer_phone: str

# ДЛЯ ОТПРАВКИ АПИ ТГ БОТА
class ProductSchema(BaseModel):
    title: str
    amount: int


class OrderInfoSchema(BaseModel):
    customer_phone: str
    order_id: str
    warehouse_name: str
    products_list: list[ProductSchema]





