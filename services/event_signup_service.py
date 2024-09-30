from datetime import UTC, datetime
from fastapi import HTTPException, status
from sqlalchemy import false
from sqlalchemy.orm import Session
from db_models.event_model import Event_DB
from db_models.event_user_model import EventUser_DB
from db_models.user_model import User_DB
from api_schemas.event_signup_schemas import EventSignupCreate, EventSignupUpdate
from user.permission import Permission


def signup_to_event(event1: Event_DB, user1: User_DB, data: EventSignupCreate, manage_permission: bool, db: Session):
    now = datetime.now(UTC)
    if event1.signup_end < now and manage_permission == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event signup deadline is passed")

    signup = EventUser_DB(user=user1, user_id=user1.id, event=event1, event_id=event1.id)

    if data.priority is not None:
        signup.priority = data.priority
    if data.group_name is not None:
        signup.group_name = data.group_name
    db.add(signup)
    db.commit()
    return signup


def signoff_from_event(
    event1: Event_DB,
    user1: User_DB,
    manage_permission: bool,
    db: Session,
):
    now = datetime.now(UTC)
    if event1.signup_end < now and manage_permission == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event signup deadline is passed")
    signup = db.query(EventUser_DB).filter_by(user_id=user1.id, event_id=event1.id).one_or_none()
    if signup is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(signup)
    db.commit()


def update_event_signup(
    event1: Event_DB, data: EventSignupUpdate, user1: User_DB, manage_permission: bool, db: Session
):
    now = datetime.now(UTC)
    if event1.signup_end < now and manage_permission == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event signup deadline is passed")
    signup = db.query(EventUser_DB).filter_by(user_id=user1.id, event_id=event1.id).one_or_none()
    if signup is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if data.priority is not None:
        signup.priority = data.priority
    if data.group_name is not None:
        signup.group_name = data.group_name

    db.commit()
