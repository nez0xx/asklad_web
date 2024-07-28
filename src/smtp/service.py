import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.core import settings

smtp_server = "smtp.mail.ru"
port = 25 # For starttls
sender_email = settings.SMTP_LOGIN
password = settings.SMTP_PASSWORD


def send_email(email_to: str, html_message: str, subject: str = "A-Склад"):

    context = ssl.create_default_context()

    server = smtplib.SMTP(smtp_server, port)

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.SMTP_LOGIN
    message["To"] = email_to
    message.attach(MIMEText(html_message, "html"))  # Пишем HTML-код здесь

    try:

        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, email_to, message.as_string())
        print("се круто"*100)
    except Exception as e:
        print(e)

    finally:
        server.quit()
