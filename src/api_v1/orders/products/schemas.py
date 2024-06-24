from pydantic import BaseModel


class ProductSchema(BaseModel):

    title: str

    amount: int

    product_id: str


class ProductUpdateSchema(BaseModel):
    title: str | None = None
    amount: int | None = None


class ProductInWarehouseSchema(BaseModel):
    title: str
    amount: int
