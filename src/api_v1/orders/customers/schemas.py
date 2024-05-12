from pydantic import BaseModel


class CustomeBaseSchema(BaseModel):
    name: str
    atomy_id: str


class CustomerGetSchema(CustomeBaseSchema):
    orders: list


class CustomersListItem(CustomeBaseSchema):
    orders_count: int


class CustomersListSchema(BaseModel):
    customers: list[CustomersListItem]
