import os
from email.mime.text import MIMEText
from mail_constants import (
    RESET_PASSWORD_LINK,
    RESET_PASSWORD_SUBJECT,
    STANDARD_SENDER,
    SUPPORT_LINK,
)
from mailer.mail_core import send_mail
from user_model import User_DB


def reset_password_mailer(user: User_DB):

    if os.getenv("ENVIRONMENT") == "testing":
        print("Email cannot be used on testing")
        return

    with open("verification-mailer.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{ user.name }}", user.first_name)
    html = html.replace("{{ reset_link }}", RESET_PASSWORD_LINK)
    html = html.replace("{{ support_link }}", SUPPORT_LINK)

    msg = MIMEText(html, "html", "utf-8")

    msg["From"] = STANDARD_SENDER
    msg["To"] = user.email
    msg["Subject"] = RESET_PASSWORD_SUBJECT

    send_mail(user, msg)  ## FIX LINK TO RESET PASSWORD
