import os
from datetime import datetime, timezone, timedelta

import jwt
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.core import settings
from src.core.settings import BASE_DIR


def encode_jwt(
        payload: dict,
        private_key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)

    expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def get_email_template(template_name: str = "template.html"):
    path = os.path.join(BASE_DIR, "templates")
    env = Environment(
        loader=FileSystemLoader(path),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template(template_name)
    return template
