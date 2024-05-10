from pydantic import BaseModel, ConfigDict, EmailStr, computed_field

from src.api_v1.auth.security import hash_password


class AuthUser(BaseModel):
    email: EmailStr

    password: str


class RegisterUser(BaseModel):
    email: EmailStr

    password: str

    @computed_field
    def hashed_password(self) -> str:
        return hash_password(self.password).decode()


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    email: str
    password: bytes


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
