from email.mime.text import MIMEText
from .mail_constants import (
    STANDARD_SENDER,
    SUPPORT_LINK,
    WELCOME_LINK,
    WELCOME_SUBJECT,
)
from mailer.mail_core import send_mail
from db_models.user_model import User_DB
import os


def welcome_mailer(user: User_DB):

    path = os.getcwd()

    with open(f"{path}/mailer/welcome-mail.html", "r", encoding="utf-8") as f:
        html = f.read()

    verification_link = f"{WELCOME_LINK}"

    html = html.replace("{{ user.name }}", user.first_name)
    html = html.replace("{{ verification_link }}", verification_link)
    html = html.replace("{{ support_link }}", SUPPORT_LINK)

    msg = MIMEText(html, "html", "utf-8")

    msg["From"] = STANDARD_SENDER
    msg["To"] = user.email
    msg["Subject"] = WELCOME_SUBJECT

    send_mail(user, msg)
