import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.api_v1.auth.crud import create_email_confirm_token
from src.api_v1.utils import encode_jwt
from src.core import settings
from src.smtp import send_email


def generate_id() -> str:
    return uuid.uuid4().hex


def create_confirm_email_link(token: str):
    return f"{settings.HOST}/#/confirm_email/{token}"


async def send_confirm_link(session: AsyncSession, email: str, user_id):
    confirm_token = await create_email_confirm_token(session=session, user_id=user_id)

    link = create_confirm_email_link(confirm_token)
    html = u'''
        <html>
            <head></head>
            <body>
            <p>Verify your account --></p>
                <a href="%s">Verify</a>
                %s
            </body>
        </html>
        ''' % (link, link)

    send_email(email, html_message=html)


