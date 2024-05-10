from pydantic import BaseModel

class ProductCreate(BaseModel):

    title: str

    amount: int

    id: str


class ProductUpdate(BaseModel):
    title: str | None = None
    amount: int | None = None
