import os
import html as python_html
from zoneinfo import ZoneInfo


from email.mime.text import MIMEText
from db_models.user_model import User_DB
from db_models.car_booking_model import CarBooking_DB
from mailer.mail_constants import (
    STANDARD_SENDER,
)
from mailer.mail_core import send_mail


def bilf_mailer(booking: CarBooking_DB) -> None:

    path = os.getcwd()

    if booking.personal:
        with open(f"{path}/mailer/bilf-mail-private.html", "r", encoding="utf-8") as f:
            html = f.read()
    else:
        with open(f"{path}/mailer/bilf-mail-council.html", "r", encoding="utf-8") as f:
            html = f.read()

    stockholm_tz = ZoneInfo("Europe/Stockholm")
    date_string = booking.start_time.astimezone(stockholm_tz).strftime("%Y-%m-%d")
    time_string = booking.start_time.astimezone(stockholm_tz).strftime("%H:%M")

    html = html.replace(
        "{{ booking.name }}", python_html.escape(booking.user.first_name + " " + booking.user.last_name, quote=True)
    )

    html = html.replace("{{ booking.date }}", date_string)

    html = html.replace("{{ booking.time }}", time_string)

    if booking.council is not None:
        html = html.replace("{{ booking.council_en }}", booking.council.name_en)
        html = html.replace("{{ booking.council_sv }}", booking.council.name_sv)

    msg = MIMEText(html, "html", "utf-8")

    msg["From"] = STANDARD_SENDER
    msg["To"] = "bil@fsektionen.se"
    if booking.personal:
        msg["Subject"] = "Ny PRIVAT bilbokning / New PRIVATE car booking"
    else:
        msg["Subject"] = "Ny kollegie-bilbokning / New council car booking"

    # This will surely be super bad
    fake_user = User_DB(
        first_name="BilF",
        last_name="BilF igen",
        telephone_number="hope this isn't validated",
        email="bil@fsektionen.se",
        hashed_password="nope",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )

    send_mail(fake_user, msg)
