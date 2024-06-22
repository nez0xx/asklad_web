from pydantic import BaseModel


class WarehouseCreateSchema(BaseModel):
    name: str
    owner_id: int


class WarehouseUpdateSchema(BaseModel):
    name: str | None = None