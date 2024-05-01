from pydantic import BaseModel

from .products.schemas import Product


class OrderCreate(BaseModel):

    customer: int

    customer_phone: str

    owner: int

    products: list[Product]