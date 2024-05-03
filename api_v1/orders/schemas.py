from pydantic import BaseModel

from .products.schemas import ProductCreate


class OrderCreate(BaseModel):

    id: str

    customer: int

    customer_phone: str

    products: list[ProductCreate]