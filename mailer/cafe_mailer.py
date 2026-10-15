import os
import html as python_html
from zoneinfo import ZoneInfo


from email.mime.text import MIMEText
from db_models.room_booking_model import RoomBooking_DB
from mailer.mail_constants import (
    STANDARD_SENDER,
)
from mailer.mail_core import send_mail_to_address

CAFE_ADDRESS = "cafe@fsektionen.se"


def cafe_mailer(booking: RoomBooking_DB, occurrences: int = 1) -> None:

    path = os.getcwd()

    with open(f"{path}/mailer/cafe-mail.html", "r", encoding="utf-8") as f:
        html = f.read()

    stockholm_tz = ZoneInfo("Europe/Stockholm")
    date_string = booking.start_time.astimezone(stockholm_tz).strftime("%Y-%m-%d")
    start_time_string = booking.start_time.astimezone(stockholm_tz).strftime("%H:%M")
    end_time_string = booking.end_time.astimezone(stockholm_tz).strftime("%H:%M")

    html = html.replace(
        "{{ booking.name }}", python_html.escape(booking.user.first_name + " " + booking.user.last_name, quote=True)
    )

    html = html.replace("{{ booking.date }}", date_string)

    html = html.replace("{{ booking.start_time }}", start_time_string)
    html = html.replace("{{ booking.end_time }}", end_time_string)

    html = html.replace("{{ booking.council_en }}", python_html.escape(booking.council.name_en, quote=True))
    html = html.replace("{{ booking.council_sv }}", python_html.escape(booking.council.name_sv, quote=True))

    html = html.replace("{{ booking.description }}", python_html.escape(booking.description or "-", quote=True))

    if occurrences > 1:
        html = html.replace("{{ booking.recurring_sv }}", f" Bokningen är återkommande med {occurrences} tillfällen.")
        html = html.replace("{{ booking.recurring_en }}", f" The booking is recurring with {occurrences} occurrences.")
    else:
        html = html.replace("{{ booking.recurring_sv }}", "")
        html = html.replace("{{ booking.recurring_en }}", "")

    msg = MIMEText(html, "html", "utf-8")

    msg["From"] = STANDARD_SENDER
    msg["To"] = CAFE_ADDRESS
    msg["Subject"] = "Ny bokning av Hilbert Café / New Hilbert Café booking"

    send_mail_to_address(CAFE_ADDRESS, msg)
