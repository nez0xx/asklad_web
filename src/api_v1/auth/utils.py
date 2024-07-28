import uuid

from src.api_v1.utils import encode_jwt
from src.core import settings
from src.smtp import send_email


def generate_id() -> str:
    return uuid.uuid4().hex


def create_confirm_email_link(token: str):
    return f"{settings.HOST}/#/confirm_email/{token}"


def send_confirm_link(email: str):
    confirm_token = encode_jwt(payload={"email": email}, expire_minutes=24 * 60)

    link = create_confirm_email_link(confirm_token)
    print(link)
    html = u'''\
        <html>
            <head></head>
            <body>
            <p>Verify your account --></p>
                <a href="%s">Verify</a>
            </body>
        </html>
        ''' % link

    send_email(email, html_message=html)


