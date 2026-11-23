import os
import html as python_html
import uuid
from datetime import datetime, timezone
from typing import Literal
from zoneinfo import ZoneInfo

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db_models.car_booking_model import CarBooking_DB
from mailer.mail_constants import (
    STANDARD_SENDER,
)
from mailer.mail_core import send_mail_to_address

BILF_ADDRESS = "bil@fsektionen.se"

BookingAction = Literal["created", "updated", "deleted", "moved_to_council"]

# Actions that remove the private booking from BilF's calendar
CANCEL_ACTIONS = ("deleted", "moved_to_council")

# Texts for private booking mails, keyed by action. {{ booking.* }} placeholders are filled in afterwards.
PRIVATE_TEXTS: dict[str, dict[str, str]] = {
    "created": {
        "subject": "Ny PRIVAT bilbokning / New PRIVATE car booking",
        "title_sv": "Ny privat bilbokning",
        "heading_sv": "En ny <strong>PRIVAT</strong> bilbokning har gjorts!",
        "body_sv": "F-älgen är bokad av {{ booking.name }} den {{ booking.date }} klockan {{ booking.time }}. HANTERA!",
        "heading_en": "A new <strong>PRIVATE</strong> booking has been made!",
        "body_en": "The car is booked by {{ booking.name }} on {{ booking.date }} at {{ booking.time }}. TAKE CARE OF IT!",
    },
    "updated": {
        "subject": "Updated private car booking / Uppdaterad privat bilbokning",
        "title_sv": "Uppdaterad privat bilbokning",
        "heading_sv": "En <strong>PRIVAT</strong> bilbokning har uppdaterats!",
        "body_sv": "Bokningen av {{ booking.name }} gäller nu den {{ booking.date }} klockan {{ booking.time }}. HANTERA!",
        "heading_en": "A <strong>PRIVATE</strong> booking has been updated!",
        "body_en": "The booking by {{ booking.name }} is now on {{ booking.date }} at {{ booking.time }}. TAKE CARE OF IT!",
    },
    "deleted": {
        "subject": "Avbokad PRIVAT bilbokning / Cancelled PRIVATE car booking",
        "title_sv": "Avbokad privat bilbokning",
        "heading_sv": "En <strong>PRIVAT</strong> bilbokning har avbokats!",
        "body_sv": "Bokningen av {{ booking.name }} den {{ booking.date }} klockan {{ booking.time }} har tagits bort.",
        "heading_en": "A <strong>PRIVATE</strong> booking has been cancelled!",
        "body_en": "The booking by {{ booking.name }} on {{ booking.date }} at {{ booking.time }} has been deleted.",
    },
    "moved_to_council": {
        "subject": "PRIVAT bilbokning flyttad till utskott / PRIVATE car booking moved to council",
        "title_sv": "Privat bilbokning flyttad till utskott",
        "heading_sv": "En <strong>PRIVAT</strong> bilbokning har gjorts om till en utskottsbokning!",
        "body_sv": (
            "Bokningen av {{ booking.name }} den {{ booking.date }} klockan {{ booking.time }} "
            "är nu en utskottsbokning för {{ booking.council_sv }}."
        ),
        "heading_en": "A <strong>PRIVATE</strong> booking has been changed to a council booking!",
        "body_en": (
            "The booking by {{ booking.name }} on {{ booking.date }} at {{ booking.time }} "
            "is now a council booking for {{ booking.council_en }}."
        ),
    },
}

# ICS SEQUENCE must increase with every revision of an event, so derive it from the send time
SEQUENCE_EPOCH = datetime(2026, 1, 1, tzinfo=timezone.utc)


def render_bilf_mail(booking: CarBooking_DB, action: BookingAction = "created") -> str:
    template_name = "bilf-mail-private.html" if booking.personal or action in CANCEL_ACTIONS else "bilf-mail-council.html"
    template_path = os.path.join(os.path.dirname(__file__), template_name)

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    for key, text in PRIVATE_TEXTS[action].items():
        html = html.replace("{{ " + key + " }}", text)

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


def fold_ics_line(line: str) -> str:
    # lines longer than 75 octets are split with CRLF followed by a space
    parts: list[str] = []
    current = ""
    limit = 75
    for char in line:
        if len((current + char).encode("utf-8")) > limit:
            parts.append(current)
            current = ""
            limit = 74  # continuation lines start with a space
        current += char
    parts.append(current)
    return "\r\n ".join(parts)


def render_bilf_ics(booking: CarBooking_DB, action: BookingAction = "created") -> str:
    now = datetime.now(timezone.utc)
    booking_id = getattr(booking, "booking_id", None)
    uid = (
        f"car-booking-{booking_id}@fsektionen.se"
        if booking_id is not None
        else f"car-booking-{uuid.uuid4()}@fsektionen.se"
    )
    dtstamp = now.strftime("%Y%m%dT%H%M%SZ")
    dtstart = booking.start_time.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dtend = booking.end_time.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sequence = int((now - SEQUENCE_EPOCH).total_seconds())
    if action in CANCEL_ACTIONS:
        method, event_status = "CANCEL", "CANCELLED"
    else:
        method, event_status = "REQUEST", "CONFIRMED" if booking.confirmed else "TENTATIVE"
    summary = {
        "created": "Private car booking",
        "updated": "Updated private car booking",
        "deleted": "Cancelled private car booking",
        "moved_to_council": "Private car booking moved to council",
    }[action]
    name = f"{booking.user.first_name} {booking.user.last_name}"
    description = (
        f"Private car booking for {name}.\n"
        f"Start: {booking.start_time.astimezone(ZoneInfo('Europe/Stockholm')).strftime('%Y-%m-%d %H:%M')}\n"
        f"End: {booking.end_time.astimezone(ZoneInfo('Europe/Stockholm')).strftime('%Y-%m-%d %H:%M')}"
    )

    def escape_ics(value: str) -> str:
        return (
            value.replace("\r", "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
        )

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//F-sektionen//Car Booking Mailer//EN",
        "CALSCALE:GREGORIAN",
        f"METHOD:{method}",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{escape_ics(summary)}",
        f"DESCRIPTION:{escape_ics(description)}",
        f"ORGANIZER;CN=F-sektionen:mailto:{STANDARD_SENDER}",
        f"ATTENDEE;CN=BilF;RSVP=FALSE:mailto:{BILF_ADDRESS}",
        f"SEQUENCE:{sequence}",
        f"STATUS:{event_status}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "".join(fold_ics_line(line) + "\r\n" for line in lines)


def build_bilf_mail(booking: CarBooking_DB, action: BookingAction = "created") -> MIMEText | MIMEMultipart:
    html = render_bilf_mail(booking, action)

    if booking.personal or action in CANCEL_ACTIONS:
        msg = MIMEMultipart("mixed")
        html_part = MIMEText(html, "html", "utf-8")
        msg.attach(html_part)

        calendar_part = MIMEText(render_bilf_ics(booking, action), "calendar", "utf-8")
        calendar_part.set_param("method", "CANCEL" if action in CANCEL_ACTIONS else "REQUEST")
        calendar_part.add_header("Content-Disposition", "attachment; filename=bilbokning.ics")
        msg.attach(calendar_part)

        msg["Subject"] = PRIVATE_TEXTS[action]["subject"]
    else:
        msg = MIMEText(html, "html", "utf-8")
        msg["Subject"] = "Ny utskotts-bilbokning / New council car booking"

    msg["From"] = STANDARD_SENDER
    msg["To"] = BILF_ADDRESS

    return msg


def send_bilf_mail(msg: MIMEText | MIMEMultipart) -> None:
    send_mail_to_address(BILF_ADDRESS, msg)


def bilf_mailer(booking: CarBooking_DB, action: BookingAction = "created") -> None:
    send_bilf_mail(build_bilf_mail(booking, action))
