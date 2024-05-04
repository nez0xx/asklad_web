from pydantic import BaseModel

from .customers.schemas import CustomerSchema
from .products.schemas import ProductCreate


class OrderCreate(BaseModel):

    id: str

    customer_phone: str

    customer: CustomerSchema

    products: list[ProductCreate]
