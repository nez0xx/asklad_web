from pydantic import BaseModel


class Table(BaseModel):
    type: str
    columns: list[str]
    font_size: int
    data: list[list]
