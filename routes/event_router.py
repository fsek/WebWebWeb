from fastapi import APIRouter, HTTPException, status
from database import DB_dependency
from db_models.event_model import Event_DB
from api_schemas.event_schemas import EventCreate, EventRead, EventUpdate
from api_schemas.user_schemas import UserRead
from db_models.event_user_model import EventUser_DB
from db_models.user_model import User_DB
from services.event_service import create_new_event, delete_event, update_event
from user.permission import Permission
import random
from typing import List

event_router = APIRouter()


@event_router.get("/", response_model=list[EventRead])
def get_all_events(db: DB_dependency):
    events = db.query(Event_DB).all()
    return events


@event_router.post("/", dependencies=[Permission.require("manage", "Event")], response_model=EventRead)
def create_event(data: EventCreate, db: DB_dependency):
    event = create_new_event(data, db)
    return event


@event_router.delete(
    "/{event_id}", dependencies=[Permission.require("manage", "Event")], status_code=status.HTTP_204_NO_CONTENT
)
def remove(event_id: int, db: DB_dependency):
    delete_event(event_id, db)
    return


@event_router.patch("/{event_id}", dependencies=[Permission.require("manage", "Event")], response_model=EventRead)
def update(event_id: int, data: EventUpdate, db: DB_dependency):
    event = update_event(event_id, data, db)
    return event


@event_router.get(
    "/all/{event_id}", dependencies=[Permission.require("manage", "Event")], response_model=list[UserRead]
)
def get_all_signups(event_id: int, db: DB_dependency):
    people_signups = db.query(EventUser_DB).filter_by(event_id=event_id).all()
    users: list[User_DB] = []
    if len(people_signups) == 0:
        return users
    users = [event_user.user for event_user in people_signups]
    return users


@event_router.get("/{event_id}", dependencies=[Permission.require("manage", "Event")], response_model=list[UserRead])
def get_random_signup(event_id: int, db: DB_dependency):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No event exist")
    people_signups = db.query(EventUser_DB).filter_by(event_id=event_id).all()
    users: list[User_DB] = []
    if len(people_signups) == 0:
        return users
    if len(people_signups) <= event.max_event_users:
        users = [event_user.user for event_user in people_signups]
        return users

    prioritized_people: List[EventUser_DB] = []
    for priority in event.priorities:
        # Assuming 'people' is a list of objects and each object has a 'priority' attribute
        prioritized_people.extend([person for person in people_signups if person.priority == priority])

    # Ensure no duplicates, maintain order
    seen: set[EventUser_DB] = set()
    unique_prioritized_people: List[EventUser_DB] = []
    for person in prioritized_people:
        if person not in seen:  # Make sure to check person.id since that's what you add to 'seen'
            seen.add(person)  # Adding person.id to the set
            people_signups.remove(person)
            unique_prioritized_people.append(person)

    # Now 'unique_prioritized_people' will have unique persons according to their id, preserving order

    places_left = event.max_event_users - len(unique_prioritized_people)
    random.seed(event_id)
    random.shuffle(people_signups)

    unique_prioritized_people.extend(people_signups[:places_left])

    users = [event_user.user for event_user in unique_prioritized_people]

    return users
