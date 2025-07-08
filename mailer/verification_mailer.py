import os
from email.mime.text import MIMEText
from database import DB_dependency
from .mail_constants import (
    STANDARD_SENDER,
    SUPPORT_LINK,
    URL,
    VERIFICATION_SUBJECT,
)
from mailer.mail_core import send_mail
from db_models.user_model import User_DB


def verification_mailer(user: User_DB, token: str):

    if os.getenv("ENVIRONMENT") == "testing":
        print("Email cannot be used on testing")
        return

    with open("/mailer/verification-mail.html", "r", encoding="utf-8") as f:
        html = f.read()

    verification_link = f"{URL}/{token}"

    html = html.replace("{{ user.name }}", user.first_name)
    html = html.replace("{{ verification_link }}", verification_link)
    html = html.replace("{{ support_link }}", SUPPORT_LINK)

    msg = MIMEText(html, "html", "utf-8")

    msg["From"] = STANDARD_SENDER
    msg["To"] = user.email
    msg["Subject"] = VERIFICATION_SUBJECT

    send_mail(user, msg)
