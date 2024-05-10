from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class SettingsWithLoadEnvVars(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f'{BASE_DIR}/.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )


class AuthJWT(BaseModel):

    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    # access_token_expire_minutes: int = 15
    access_token_expire_minutes: int = 60


class Settings(SettingsWithLoadEnvVars):

    auth_jwt: AuthJWT = AuthJWT()

    db_url: str = f'sqlite+aiosqlite:///{BASE_DIR}/db.sqlite3'

    SMTP_LOGIN: str
    SMTP_PASSWORD: str

    TEST: str

settings = Settings()
