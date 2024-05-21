from pydantic import BaseModel


class CustomerBaseSchema(BaseModel):
    name: str
    atomy_id: str


class CustomerGetSchema(CustomerBaseSchema):
    orders: list


class CustomersListItem(CustomerBaseSchema):
    orders_count: int


class CustomersListSchema(BaseModel):
    customers: list[CustomersListItem]
