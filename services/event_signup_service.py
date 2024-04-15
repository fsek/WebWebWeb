from datetime import UTC, datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from db_models.event_model import Event_DB
from db_models.event_user_model import EventUser_DB
from db_models.user_model import User_DB


def signup_to_event(event1: Event_DB, user1: User_DB, db: Session):
    now = datetime.now(UTC)
    if event1.signup_start < now:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event signup deadline is passed")

    signup = EventUser_DB(user=user1,user_id=user1.id, event=event1, event_id=event1.id)
    db.add(signup)
    db.commit()
    return signup
