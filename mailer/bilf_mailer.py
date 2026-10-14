import os
import html as python_html
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db_models.car_booking_model import CarBooking_DB
from mailer.mail_constants import (
    STANDARD_SENDER,
)
from mailer.mail_core import send_mail_to_address


def render_bilf_mail(booking: CarBooking_DB) -> str:
    template_name = "bilf-mail-private.html" if booking.personal else "bilf-mail-council.html"
    template_path = os.path.join(os.path.dirname(__file__), template_name)

    with open(template_path, "r", encoding="utf-8") as f:
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
    else:
        html = html.replace("{{ booking.council_en }}", "Unknown council")
        html = html.replace("{{ booking.council_sv }}", "Okänt utskott")

    return html


def render_bilf_ics(booking: CarBooking_DB, is_update: bool = False) -> str:
    booking_id = getattr(booking, "booking_id", None)
    uid = (
        f"car-booking-{booking_id}@fsektionen.se"
        if booking_id is not None
        else f"car-booking-{uuid.uuid4()}@fsektionen.se"
    )
    dtstamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dtstart = booking.start_time.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dtend = booking.end_time.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary = "Updated private car booking" if is_update else "Private car booking"
    name = f"{booking.user.first_name} {booking.user.last_name}"
    description = (
        f"Private car booking for {name}.\n"
        f"Start: {booking.start_time.astimezone(ZoneInfo('Europe/Stockholm')).strftime('%Y-%m-%d %H:%M')}\n"
        f"End: {booking.end_time.astimezone(ZoneInfo('Europe/Stockholm')).strftime('%Y-%m-%d %H:%M')}"
    )

    def escape_ics(value: str) -> str:
        return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    return (
        "\n".join(
            [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//F-sektionen//Car Booking Mailer//EN",
                "CALSCALE:GREGORIAN",
                "METHOD:REQUEST",
                "BEGIN:VEVENT",
                f"UID:{uid}",
                f"DTSTAMP:{dtstamp}",
                f"DTSTART:{dtstart}",
                f"DTEND:{dtend}",
                f"SUMMARY:{escape_ics(summary)}",
                f"DESCRIPTION:{escape_ics(description)}",
                "ORGANIZER:mailto:bil@fsektionen.se",
                f"ATTENDEE;CN={escape_ics(name)}:mailto:bil@fsektionen.se",
                f"SEQUENCE:{1 if is_update else 0}",
                "STATUS:CONFIRMED",
                "END:VEVENT",
                "END:VCALENDAR",
            ]
        )
        + "\n"
    )


def bilf_mailer(booking: CarBooking_DB, is_update: bool = False) -> None:
    html = render_bilf_mail(booking)

    if booking.personal:
        msg = MIMEMultipart("mixed")
        html_part = MIMEText(html, "html", "utf-8")
        msg.attach(html_part)

        calendar_part = MIMEText(render_bilf_ics(booking, is_update=is_update), "calendar", "utf-8")
        calendar_part.set_param("method", "REQUEST")
        calendar_part.add_header("Content-Disposition", "attachment; filename=bilbokning.ics")
        msg.attach(calendar_part)

        msg["Subject"] = (
            "Updated private car booking / Uppdaterad privat bilbokning"
            if is_update
            else ("Ny PRIVAT bilbokning / New PRIVATE car booking")
        )
    else:
        msg = MIMEText(html, "html", "utf-8")
        msg["Subject"] = "Ny kollegie-bilbokning / New council car booking"

    msg["From"] = STANDARD_SENDER
    msg["To"] = "bil@fsektionen.se"

    send_mail_to_address("bil@fsektionen.se", msg)
