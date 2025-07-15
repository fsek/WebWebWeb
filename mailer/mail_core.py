from email.mime.text import MIMEText
import os
import smtplib

from mailer.mail_constants import SMTP_SERVER, STANDARD_SENDER
from db_models.user_model import User_DB


def send_mail(user: User_DB, msg: MIMEText):

    if os.getenv("ENVIRONMENT") != "production":
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
