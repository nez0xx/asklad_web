from pydantic import BaseModel


class WarehouseCreateSchema(BaseModel):
    name: str
    owner_id: int


class EmployeeAddSchema(BaseModel):
    user_id: int
    warehouse_id: int


class EmployeeDeleteSchema(EmployeeAddSchema):
    pass
