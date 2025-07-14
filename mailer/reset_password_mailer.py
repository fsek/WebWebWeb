from email.mime.text import MIMEText
import os
from mailer.mail_constants import (
    RESET_PASSWORD_LINK,
    RESET_PASSWORD_SUBJECT,
    STANDARD_SENDER,
    SUPPORT_LINK,
)
from mailer.mail_core import send_mail
from db_models.user_model import User_DB


def reset_password_mailer(user: User_DB, token: str):

    path = os.getcwd()

    with open(f"{path}/mailer/reset-password-mail.html", "r", encoding="utf-8") as f:
        html = f.read()

    reset_password_url = f"{RESET_PASSWORD_LINK}/{token}"

    html = html.replace("{{ user.name }}", user.first_name)
    html = html.replace("{{ reset_link }}", reset_password_url)
    html = html.replace("{{ support_link }}", SUPPORT_LINK)

    msg = MIMEText(html, "html", "utf-8")

    msg["From"] = STANDARD_SENDER
    msg["To"] = user.email
    msg["Subject"] = RESET_PASSWORD_SUBJECT

    send_mail(user, msg)  ## FIX LINK TO RESET PASSWORD
