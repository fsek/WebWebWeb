from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from database import DB_dependency
from db_models.event_model import Event_DB
from db_models.user_model import User_DB
from services.event_signup_service import signup_to_event
from user.permission import Permission
from api_schemas.event_signup import EventSignupCreate


event_signup_router = APIRouter()


# Sing current user up to an event
@event_signup_router.post("/{event_id}")
def signup_route(event_id: int, signup: EventSignupCreate, me: Annotated[User_DB, Permission.member()], db: DB_dependency):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    signup_to_event(event, me, signup, db)
    return
