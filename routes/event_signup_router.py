from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from api_schemas.user_schemas import UserRead
from database import DB_dependency
from db_models.event_model import Event_DB
from db_models.event_user_model import EventUser_DB
from db_models.user_model import User_DB
from services.event_signup_service import signup_to_event, signoff_from_event, update_event_signup
from user.permission import Permission
from api_schemas.event_signup_schemas import EventSignupCreate, EventSignupRead, EventSignupUpdate, EventSignupDelete
from pydantic_extra_types.phone_numbers import PhoneNumber
from api_schemas.event_schemas import EventRead

event_signup_router = APIRouter()


# Sing current user up to an event
@event_signup_router.post("/{event_id}", response_model=EventRead)
def signup_route(
    event_id: int,
    data: EventSignupCreate,
    me: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Event")],
    db: DB_dependency,
):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if data.user_id is None or data.user_id == me.id:
        return signup_to_event(event, me, data, manage_permission, db)

    if manage_permission == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Check your permissions mate")

    user = db.query(User_DB).filter_by(id=data.user_id).one_or_none()
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    return signup_to_event(event, user, data, manage_permission, db)


@event_signup_router.delete("/{event_id}", response_model=EventRead)
def signoff_route(
    event_id: int,
    data: EventSignupDelete,
    me: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Event")],
    db: DB_dependency,
):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if data.user_id is None or data.user_id == me.id:
        return signoff_from_event(event, me.id, manage_permission, db)

    if manage_permission == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Check your permissions mate")

    return signoff_from_event(event, data.user_id, manage_permission, db)


@event_signup_router.patch("/{event_id}", response_model=EventRead)
def update_signup(
    event_id: int,
    data: EventSignupUpdate,
    me: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Event")],
    db: DB_dependency,
):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if data.user_id is None or data.user_id == me.id:
        return update_event_signup(event, data, me.id, manage_permission, db)

    if manage_permission == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Check your permissions mate")

    return update_event_signup(event, data, data.user_id, manage_permission, db)


# @event_signup_router.get("/{event_id}", response_model=list[EventSignupRead])
# def get_all_signups(event_id: int, db: DB_dependency):
#     signups = db.query(EventUser_DB).filter(EventUser_DB.event_id == event_id).all()
#     if not signups:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No signups found for this event")
#     # Assuming you have logic to convert EventUser_DB instances to UserRead instances
#     return [convert_event_user_to_signup_read(signup) for signup in signups]


# def convert_event_user_to_signup_read(event_user: EventUser_DB) -> EventSignupRead:
#     # Convert EventUser_DB instance to EventSignupRead based on your application's logic
#     return EventSignupRead(
#         id=event_user.user_id,
#         first_name=event_user.user.first_name,
#         last_name=event_user.user.last_name,
#         email=event_user.user.email,  # Assuming there is an email field in User_DB
#         telephone_number=PhoneNumber(event_user.user.telephone_number),
#         start_year=event_user.user.start_year,
#         account_created=event_user.user.account_created,
#         program=event_user.user.program,
#         priority=event_user.priority,
#         group_name=event_user.group_name,
#     )
