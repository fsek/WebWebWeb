from datetime import UTC, timedelta, datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from db_models.event_model import Event_DB
from api_schemas.event_schemas import EventCreate


def create_new_event(data: EventCreate, db: Session):
    # We want to talk in UTC times to be clear and avoid timezone confusion
    zero_dt = timedelta(0)
    if data.starts_at.utcoffset() != zero_dt or data.ends_at.utcoffset() != zero_dt:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Datetimes must be UTC")

    start = data.starts_at.astimezone(UTC)
    end = data.ends_at.astimezone(UTC)
    start = start.replace(second=0, microsecond=0)  # round down to whole minutes
    end = end.replace(second=0, microsecond=0)

    if end <= start:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Start date must be before end")

    if start < datetime.now(UTC):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event start cannot be in the past")

    event = Event_DB(
        starts_at=start,
        ends_at=end,
        title_sv=data.title_sv,
        title_en=data.title_en,
        description_sv=data.description_sv,
        description_en=data.description_en,
        council_id=data.council_id,
        signup_start=data.signup_start,
        signup_end=data.signup_end,
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
