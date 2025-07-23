from email.mime.text import MIMEText
import os
from typing import Optional
from mailer.mail_constants import (
    EMAIL_CHANGED_SUBJECT,
    STANDARD_SENDER,
    SUPPORT_LINK,
)
from mailer.mail_core import send_mail
from db_models.user_model import User_DB


def mask_email(email: Optional[str]) -> str:
    if not email:
        return "***@***.***"  # fallback

    try:
        local, domain = email.split("@")
        if len(local) <= 2:
            return f"{local[0]}***@{domain}"
        else:
            return f"{local[0]}***{local[-1]}@{domain}"
    except (ValueError, IndexError):
        return "***@***.***"  # fallback in case of an invalid email format


def email_changed_mailer(user: User_DB, new_email: str, old_email: str):
    path = os.getcwd()

    with open(f"{path}/mailer/email-changed-mail.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{ user.name }}", user.first_name)
    html = html.replace("{{ new_email_masked }}", mask_email(new_email))
    html = html.replace("{{ support_link }}", SUPPORT_LINK)

    msg = MIMEText(html, "html", "utf-8")

    msg["From"] = STANDARD_SENDER
    msg["To"] = old_email
    msg["Subject"] = EMAIL_CHANGED_SUBJECT

    send_mail(user, msg)
