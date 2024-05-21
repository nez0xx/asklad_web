from pydantic import BaseModel

from .customers.schemas import CustomerBaseSchema
from .products.schemas import ProductBase


class OrderBase(BaseModel):

    warehouse_id: int

    atomy_id: str

    customer_phone: str

    customer: CustomerBaseSchema

    products: list[ProductBase]


class OrderListItem(BaseModel):

    customer_phone: str





