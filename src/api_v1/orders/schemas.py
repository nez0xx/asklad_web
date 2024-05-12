from pydantic import BaseModel

from .customers.schemas import CustomeBaseSchema
from .products.schemas import ProductCreate


class OrderCreate(BaseModel):

    id: str

    customer_phone: str

    customer: CustomeBaseSchema

    products: list[ProductCreate]

class OrderListItem(BaseModel):

    customer_phone: str

