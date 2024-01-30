from datetime import UTC, datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from db_models.event_model import Event_DB
from api_schemas.event_schemas import EventCreate, EventUpdate
from helpers.date_util import force_utc, round_whole_minute


def create_new_event(data: EventCreate, db: Session):
    force_utc(data.starts_at)
    force_utc(data.ends_at)
    force_utc(data.signup_start)
    force_utc(data.signup_end)

    start = round_whole_minute(data.starts_at)
    end = round_whole_minute(data.ends_at)
    signup_start = round_whole_minute(data.signup_start)
    signup_end = round_whole_minute(data.signup_end)

    if end <= start:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Start date must be before end")

    if start < datetime.now(UTC):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event start cannot be in the past, silly.")

    event = Event_DB(
        starts_at=start,
        ends_at=end,
        title_sv=data.title_sv,
        title_en=data.title_en,
        description_sv=data.description_sv,
        description_en=data.description_en,
        council_id=data.council_id,
        signup_start=signup_start,
        signup_end=signup_end,
    )
    db.add(event)
    db.commit()

    return event


def delete_event(event_id: int, db: Session):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(event)
    db.commit()


def update_event(event_id: int, data: EventUpdate, db: Session):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if len(data.description_en) != 0:
        event.description_en = data.description_en
    if len(data.description_sv) != 0:
        event.description_sv = data.description_sv
    if len(data.title_en) != 0:
        event.title_en = data.title_en
    if len(data.title_sv) != 0:
        event.title_sv = data.title_sv
    db.commit()
    return event
