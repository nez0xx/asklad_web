from pydantic import BaseModel


class CustomerSchema(BaseModel):
    name: str
    id: str
