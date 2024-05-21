from pydantic import BaseModel


class WarehouseCreateSchema(BaseModel):
    name: str
    owner_id: int


class EmployeeAddSchema(BaseModel):
    email: str
    warehouse_name: str


class EmployeeDeleteSchema(EmployeeAddSchema):
    pass
