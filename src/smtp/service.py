import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.core import settings

smtp_server = settings.SMTP_HOST
port = settings.SMTP_PORT
sender_email = settings.SMTP_LOGIN
password = settings.SMTP_PASSWORD


def send_email(email_to: str, html_message: str, subject: str = "A-Склад"):
    server = smtplib.SMTP(smtp_server, port)
    print(smtp_server, port, sender_email, password)
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = email_to
    message.attach(MIMEText(html_message, "html"))  # Пишем HTML-код здесь

    try:
        server.ehlo()
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, email_to, message.as_string())
    except Exception as e:
        print(e)

    finally:
        server.quit()
