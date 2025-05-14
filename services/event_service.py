from datetime import UTC, datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from db_models.council_model import Council_DB
from db_models.event_model import Event_DB
from api_schemas.event_schemas import EventCreate, EventUpdate
from db_models.priority_model import Priority_DB
from helpers.date_util import round_whole_minute


def create_new_event(data: EventCreate, db: Session):
    start = round_whole_minute(data.starts_at)
    end = round_whole_minute(data.ends_at)
    signup_start = round_whole_minute(data.signup_start)
    signup_end = round_whole_minute(data.signup_end)

    if end <= start:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Start date must be before end")

    if start < datetime.now(UTC):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event start cannot be in the past, silly.")

    # Check if council exists. It's just some extra validation
    council = db.query(Council_DB).filter_by(id=data.council_id).one_or_none()
    if council is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "That council does not exist")

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
        max_event_users=data.max_event_users,
        all_day=data.all_day,
        signup_not_opened_yet=data.signup_not_opened_yet,
        recurring=data.recurring,
        drink=data.drink,
        food=data.food,
        cash=data.cash,
        closed=data.closed,
        can_signup=data.can_signup,
        drink_package=data.drink_package,
        location=data.location,
        is_nollning_event=data.is_nollning_event,
    )
    db.add(event)  # This adds the event itself to the session
    db.flush()  # This is optional but can be helpful to ensure 'event.id' is set if used immediately after

    priorities = [Priority_DB(priority=priority, event_id=event.id) for priority in data.priorities]

    # Add each priority to the session individually
    for priority in priorities:
        db.add(priority)
    db.commit()  # Commit all changes to the database

    db.refresh(event)

    return event


def delete_event(event_id: int, db: Session):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(event)
    db.commit()

    return event


def update_event(event_id: int, data: EventUpdate, db: Session):

    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()

    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    for var, value in vars(data).items():
        setattr(event, var, value) if value is not None else None

    db.commit()
    return event
