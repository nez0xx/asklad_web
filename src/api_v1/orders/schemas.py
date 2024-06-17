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





