import os
import html as python_html
from zoneinfo import ZoneInfo


from email.mime.text import MIMEText
from db_models.car_booking_model import CarBooking_DB
from mailer.mail_constants import (
    STANDARD_SENDER,
)
from mailer.mail_core import send_mail_to_adress


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
        html = html.replace("{{ booking.council_en }}", python_html.escape(booking.council.name_en, quote=True))
        html = html.replace("{{ booking.council_sv }}", python_html.escape(booking.council.name_sv, quote=True))

    msg = MIMEText(html, "html", "utf-8")

    msg["From"] = STANDARD_SENDER
    msg["To"] = "bil@fsektionen.se"
    if booking.personal:
        msg["Subject"] = "Ny PRIVAT bilbokning / New PRIVATE car booking"
    else:
        msg["Subject"] = "Ny kollegie-bilbokning / New council car booking"

    send_mail_to_adress("bil@fsektionen.se", msg)
