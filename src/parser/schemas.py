from pydantic import BaseModel


class Product(BaseModel):
    atomy_id: str
    title: str
    amount: int


class Customer(BaseModel):
    name: str
    atomy_id: str


class Order(BaseModel):
    atomy_id: str
    customer: Customer
    customer_phone: str
    products: list[Product]


class UnitedOrder(BaseModel):
    united_order_id: str
    orders: list[Order]