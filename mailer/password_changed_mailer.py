from email.mime.text import MIMEText
import os
from mailer.mail_constants import (
    PASSWORD_CHANGED_SUBJECT,
    STANDARD_SENDER,
    SUPPORT_LINK,
)
from mailer.mail_core import send_mail
from db_models.user_model import User_DB


def password_changed_mailer(user: User_DB):

    path = os.getcwd()

    with open(f"{path}/mailer/password-changed-mail.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{ user.name }}", user.first_name)
    html = html.replace("{{ support_link }}", SUPPORT_LINK)

    msg = MIMEText(html, "html", "utf-8")

    msg["From"] = STANDARD_SENDER
    msg["To"] = user.email
    msg["Subject"] = PASSWORD_CHANGED_SUBJECT

    send_mail(user, msg)
