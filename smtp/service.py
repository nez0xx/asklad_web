import smtplib
import ssl
from core.settings import settings

smtp_server = "smtp.mail.ru"
port = 25 # For starttls
sender_email = settings.SMTP_LOGIN
password = settings.SMTP_PASSWORD


def send_message(email_to: str, message: str):

    context = ssl.create_default_context()

    server = smtplib.SMTP(smtp_server, port)

    try:

        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, email_to, msg=message)

    except Exception as e:
        print(e)

    finally:
        server.quit()
