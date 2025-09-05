from email.mime.text import MIMEText

from nomination_model import Nomination_DB
from .mail_constants import STANDARD_SENDER, ELECTION_SUPPORT_LINK, CANDIDACY_LINK, CANDIDACY_SUBJECT, URL, STAGE_URL
from mailer.mail_core import send_mail
from db_models.user_model import User_DB
import os
import html as python_html
from zoneinfo import ZoneInfo


def nomination_mailer(user: User_DB, nomination: Nomination_DB):

    path = os.getcwd()

    with open(f"{path}/mailer/nomination-mail.html", "r", encoding="utf-8") as f:
        html = f.read()

    if os.getenv("ENVIRONMENT") == "stage":
        candidacy_link = f"{STAGE_URL}{CANDIDACY_LINK}"
    else:
        candidacy_link = f"{URL}{CANDIDACY_LINK}"

    html = html.replace("{{ user.name }}", python_html.escape(user.first_name))
    html = html.replace("{{ user.email }}", python_html.escape(user.email))
    html = html.replace("{{ position_name_sv }}", python_html.escape(nomination.election_post.post.name_sv))
    html = html.replace("{{ position_name_en }}", python_html.escape(nomination.election_post.post.name_en))
    html = html.replace("{{ candidacy_link }}", candidacy_link)

    stockholm_tz = ZoneInfo("Europe/Stockholm")
    dt = nomination.sub_election.end_time
    html = html.replace("{{ deadline_date }}", dt.astimezone(stockholm_tz).strftime("%Y-%m-%d %H:%M"))
    html = html.replace("{{ election_admin_email }}", ELECTION_SUPPORT_LINK)

    msg = MIMEText(html, "html", "utf-8")

    msg["From"] = STANDARD_SENDER
    msg["To"] = user.email
    msg["Subject"] = CANDIDACY_SUBJECT

    send_mail(user, msg)
