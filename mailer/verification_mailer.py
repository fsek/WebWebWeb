from email.mime.text import MIMEText
import os
from .mail_constants import (
    STANDARD_SENDER,
    SUPPORT_LINK,
    VERIFICATION_LINK,
    VERIFICATION_SUBJECT,
    URL,
    STAGE_URL,
)
from mailer.mail_core import send_mail
from db_models.user_model import User_DB
import html as python_html


def verification_mailer(user: User_DB, token: str):

    path = os.getcwd()

    with open(f"{path}/mailer/verification-mail.html", "r", encoding="utf-8") as f:
        html = f.read()

    if os.getenv("ENVIRONMENT") == "stage":
        verification_link = f"{STAGE_URL}{VERIFICATION_LINK}{token}"
    else:
        verification_link = f"{URL}{VERIFICATION_LINK}{token}"

    html = html.replace("{{ user.name }}", python_html.escape(user.first_name))
    html = html.replace("{{ verification_link }}", verification_link)
    html = html.replace("{{ support_link }}", SUPPORT_LINK)

    msg = MIMEText(html, "html", "utf-8")

    msg["From"] = STANDARD_SENDER
    msg["To"] = user.email
    msg["Subject"] = VERIFICATION_SUBJECT

    send_mail(user, msg)
