from pydantic import BaseModel
from src.api_v1.orders.schemas import OrderSchema


class Product(BaseModel):
    product_id: str
    title: str
    amount: int


class Customer(BaseModel):
    name: str
    atomy_id: str

'''
class OrderSchema(BaseModel):
    order_id: str
    customer_name: str
    customer_id: str
    customer_phone: str
    products: list[Product]
'''

class UnitedOrder(BaseModel):
    united_order_id: str
    orders: list[OrderSchema]
