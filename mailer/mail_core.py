from email.mime.text import MIMEText
import os
import smtplib

from pydantic import EmailStr

from mailer.mail_constants import SMTP_SERVER, STANDARD_SENDER
from db_models.user_model import User_DB


def send_mail(user: User_DB, msg: MIMEText):
    env = os.getenv("ENVIRONMENT")

    if env != "production" and env != "stage":
        print("Email cannot be used on testing")
        return

    try:
        # Create an SMTP session
        with smtplib.SMTP(SMTP_SERVER, smtplib.SMTP_PORT) as server:
            server.starttls()
            server.sendmail(STANDARD_SENDER, user.email, msg.as_string())
            print(f"Email sent successfully to {user.first_name}")
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_mail_to_adress(adress: EmailStr, msg: MIMEText):
    env = os.getenv("ENVIRONMENT")

    if env != "production" and env != "stage":
        print("Email cannot be used on testing")
        return

    try:
        # Create an SMTP session
        with smtplib.SMTP(SMTP_SERVER, smtplib.SMTP_PORT) as server:
            server.starttls()
            server.sendmail(STANDARD_SENDER, adress, msg.as_string())
            print(f"Email sent successfully to adress {adress}")
    except Exception as e:
        print(f"Failed to send email: {e}")
