from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str
    password: bytes


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
