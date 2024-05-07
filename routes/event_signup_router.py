from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from api_schemas.user_schemas import UserRead, UserSignupRead
from database import DB_dependency
from db_models.event_model import Event_DB
from db_models.event_user_model import EventUser_DB
from db_models.user_model import User_DB
from services.event_signup_service import signup_to_event
from user.permission import Permission
from api_schemas.event_signup import EventSignupCreate
from pydantic_extra_types.phone_numbers import PhoneNumber
from api_schemas.event_schemas import EventRead

event_signup_router = APIRouter()


# Sing current user up to an event
@event_signup_router.post("/{event_id}", response_model=EventRead)
def signup_route(event_id: int, signup: EventSignupCreate, me: Annotated[User_DB, Permission.member()], db: DB_dependency):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    signup_to_event(event, me, signup, db)
    return event

@event_signup_router.get("/{event_id}", response_model=list[UserSignupRead])
def get_all_signups(event_id: int, db: DB_dependency):
    signups = db.query(EventUser_DB).filter(EventUser_DB.event_id == event_id).all()
    if not signups:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No signups found for this event")
    # Assuming you have logic to convert EventUser_DB instances to UserRead instances
    return [convert_event_user_to_user_read(signup) for signup in signups]

def convert_event_user_to_user_read(event_user: EventUser_DB) -> UserSignupRead:
    # Convert EventUser_DB instance to UserRead based on your application's logic
    return UserSignupRead(
        id=event_user.user_id,
        first_name=event_user.user.first_name,
        last_name=event_user.user.last_name,
        email=event_user.user.email,  # Assuming there is an email field in User_DB
        telephone_number=PhoneNumber(event_user.user.telephone_number),
        start_year=event_user.user.start_year,
        account_created=event_user.user.account_created,
    )