from pydantic import BaseModel


class WarehouseCreateSchema(BaseModel):
    name: str
    owner_id: int


class EmployeeAddSchema(BaseModel):
    employee_id: int
    warehouse_name: str


class EmployeeDeleteSchema(EmployeeAddSchema):
    pass
