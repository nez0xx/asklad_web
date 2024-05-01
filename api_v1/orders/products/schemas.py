from pydantic import BaseModel

class Product(BaseModel):

    title: str

    amount: int
