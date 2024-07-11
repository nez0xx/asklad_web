import os
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent
DOTENV = os.path.join(BASE_DIR, ".env")


class SettingsWithLoadEnvVars(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_file_encoding='utf-8',
        extra='ignore'
    )


class AuthJWT(BaseModel):

    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 60*24*3
    refresh_token_expire_minutes: int = 60*24*7


class Settings(SettingsWithLoadEnvVars):

    auth_jwt: AuthJWT = AuthJWT()

    db_url: str = 'postgresql+asyncpg://postgres:root@localhost:5432/db_api'
    SMTP_LOGIN: str
    SMTP_PASSWORD: str

    HOST: str
    NOTIFICATION_BOT_URL: str
    test_db_url: str = f'sqlite+aiosqlite:///{BASE_DIR}/test_db.sqlite3'


settings = Settings()
