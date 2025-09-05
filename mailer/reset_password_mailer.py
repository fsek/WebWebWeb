from email.mime.text import MIMEText
import os
from mailer.mail_constants import (
    RESET_PASSWORD_LINK,
    RESET_PASSWORD_SUBJECT,
    STANDARD_SENDER,
    SUPPORT_LINK,
    URL,
    STAGE_URL,
)
from mailer.mail_core import send_mail
from db_models.user_model import User_DB
import html as python_html


def reset_password_mailer(user: User_DB, token: str):

    path = os.getcwd()

    with open(f"{path}/mailer/reset-password-mail.html", "r", encoding="utf-8") as f:
        html = f.read()

    if os.getenv("ENVIRONMENT") == "stage":
        reset_password_url = f"{STAGE_URL}{RESET_PASSWORD_LINK}{token}"
    else:
        reset_password_url = f"{URL}{RESET_PASSWORD_LINK}{token}"

    html = html.replace("{{ user.name }}", python_html.escape(user.first_name))
    html = html.replace("{{ reset_link }}", reset_password_url)
    html = html.replace("{{ support_link }}", SUPPORT_LINK)

    msg = MIMEText(html, "html", "utf-8")

    msg["From"] = STANDARD_SENDER
    msg["To"] = user.email
    msg["Subject"] = RESET_PASSWORD_SUBJECT

    send_mail(user, msg)  ## FIX LINK TO RESET PASSWORD
