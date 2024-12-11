from datetime import UTC, datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from db_models.event_model import Event_DB
from db_models.event_user_model import EventUser_DB
from db_models.user_model import User_DB
from api_schemas.event_signup_schemas import EventSignupCreate, EventSignupUpdate
from user.permission import Permission


def signup_to_event(event: Event_DB, user: User_DB, data: EventSignupCreate, manage_permission: bool, db: Session):
    now = datetime.now(UTC)
    if event.signup_end < now and manage_permission == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event signup deadline is passed")

    signup = EventUser_DB(user=user, user_id=user.id, event=event, event_id=event.id)

    if data.priority is not None:
        signup.priority = data.priority
    if data.group_name is not None:
        signup.group_name = data.group_name
    db.add(signup)
    db.commit()
    return signup


def signoff_from_event(
    event: Event_DB,
    user_id: int,
    manage_permission: bool,
    db: Session,
):
    now = datetime.now(UTC)
    if event.signup_end < now and manage_permission == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event signup deadline is passed")
    signup = db.query(EventUser_DB).filter_by(user_id=user_id, event_id=event.id).one_or_none()
    if signup is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(signup)
    db.commit()
    return signup


def update_event_signup(event: Event_DB, data: EventSignupUpdate, user_id: int, manage_permission: bool, db: Session):
    now = datetime.now(UTC)
    if event.signup_end < now and manage_permission == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event signup deadline is passed")
    signup = db.query(EventUser_DB).filter_by(user_id=user_id, event_id=event.id).one_or_none()
    if signup is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if data.priority is not None:
        signup.priority = data.priority
    if data.group_name is not None:
        signup.group_name = data.group_name

    db.commit()
    db.refresh(event)
    return signup
