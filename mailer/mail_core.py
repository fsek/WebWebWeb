from email.mime.text import MIMEText
import smtplib

from mailer.mail_constants import SMTP_SERVER, STANDARD_SENDER
from db_models.user_model import User_DB


def send_mail(user: User_DB, msg: MIMEText):
    try:
        # Create an SMTP session
        with smtplib.SMTP(SMTP_SERVER, smtplib.SMTP_PORT) as server:
            server.starttls()
            server.sendmail(STANDARD_SENDER, user.email, msg.as_string())
            print(f"Email sent successfully to {user.first_name}")
    except Exception as e:
        print(f"Failed to send email: {e}")
