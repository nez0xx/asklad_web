from pydantic import BaseModel

class ProductCreate(BaseModel):

    title: str

    amount: int

    atomy_id: str


class ProductUpdate(BaseModel):
    title: str | None = None
    amount: int | None = None
