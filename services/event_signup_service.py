from datetime import UTC, datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from db_models.event_model import Event_DB
from db_models.event_signup_model import EventSignup_DB
from db_models.user_model import User_DB


def signup_to_event(event: Event_DB, user: User_DB, db: Session):
    now = datetime.now(UTC)
    if event.signup_start < now:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event signup deadline is passed")

    signup = EventSignup_DB(user=user, event=event)
    db.add(signup)
    db.commit()
    return signup
