from pydantic import BaseModel

class ProductBase(BaseModel):

    title: str

    amount: int

    atomy_id: str


class ProductUpdateSchema(BaseModel):
    title: str | None = None
    amount: int | None = None
