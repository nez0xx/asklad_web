from pydantic import BaseModel

class ProductCreate(BaseModel):

    title: str

    amount: int

    id: str
