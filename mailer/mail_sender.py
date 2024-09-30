import smtplib
from email.mime.text import MIMEText

from api_schemas.mail_schema import MailSend
from dotenv import load_dotenv
import os


def send_mail(data: MailSend) -> bool:
    msg = MIMEText(data.body)
    msg["From"] = data.sender
    msg["To"] = data.receiver
    msg["Subject"] = data.subject

    # SMTP configuration
    load_dotenv()  # This loads the environment variables from the .env file
    smtp_server = os.getenv("SMTP_SERVER", "failed")
    smtp_port = int(os.getenv("SMTP_PORT", 0))

    if (smtp_port != 0) | (smtp_server == "failed"):
        return False

    try:
        # Create an SMTP session
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.sendmail(data.sender, data.receiver, msg.as_string())
            return True
    except Exception as e:
        return False
