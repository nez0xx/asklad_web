from pydantic import BaseModel


class CustomerSchema(BaseModel):
    name: str
    atomy_id: str


class CustomersListItem(CustomerSchema):
    orders_count: int


class CustomersListSchema(BaseModel):
    customers: list[CustomersListItem]
