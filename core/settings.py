from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent


class AuthJWT(BaseModel):

    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    # access_token_expire_minutes: int = 15
    access_token_expire_minutes: int = 60


class Settings(BaseSettings):

    auth_jwt: AuthJWT = AuthJWT()

    db_url: str = f'sqlite+aiosqlite:///{BASE_DIR}/db.sqlite3'

    SMTP_LOGIN: str = "chugainov266@mail.ru"
    SMTP_PASSWORD: str = "qgQqrFxyqW5UHebRzHqG"

settings = Settings()
