from io import StringIO
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from psycopg import IntegrityError
from api_schemas.tag_schema import EventTagRead
from database import DB_dependency
from db_models.event_model import Event_DB
from api_schemas.event_schemas import AddEventTag, EventCreate, EventRead, EventUpdate
from api_schemas.user_schemas import UserRead
from db_models.event_user_model import EventUser_DB
from db_models.user_model import User_DB
from db_models.event_tag_model import EventTag_DB
from services.event_service import create_new_event, delete_event, update_event
from user.permission import Permission
import random
from typing import List, get_args
from helpers.types import MEMBER_ROLES

import pandas as pd

event_router = APIRouter()


@event_router.get("/", response_model=list[EventRead])
def get_all_events(db: DB_dependency):
    events = db.query(Event_DB).all()
    return events


@event_router.get("/priorities", response_model=list[str])
def get_event_priorities():
    # Extract literal values using typing
    member_roles = get_args(MEMBER_ROLES)
    return list(member_roles)


@event_router.get("/{eventId}", response_model=EventRead)
def get_single_event(db: DB_dependency, eventId: int):
    event = db.query(Event_DB).filter(Event_DB.id == eventId).one_or_none()

    if not event:
        raise HTTPException(404, detail="Event not found")

    return event


@event_router.post("/", dependencies=[Permission.require("manage", "Event")], response_model=EventRead)
def create_event(data: EventCreate, db: DB_dependency):
    event = create_new_event(data, db)
    return event


@event_router.delete("/{event_id}", dependencies=[Permission.require("manage", "Event")], response_model=EventRead)
def event_remove(event_id: int, db: DB_dependency):
    return delete_event(event_id, db)


@event_router.patch("/{event_id}", dependencies=[Permission.require("manage", "Event")], response_model=EventRead)
def event_update(event_id: int, data: EventUpdate, db: DB_dependency):
    event = update_event(event_id, data, db)
    return event


@event_router.get(
    "/event-signups/all/{event_id}", dependencies=[Permission.require("manage", "Event")], response_model=list[UserRead]
)
def get_all_event_signups(event_id: int, db: DB_dependency):
    people_signups = db.query(EventUser_DB).filter_by(event_id=event_id).all()
    users: list[User_DB] = []
    if len(people_signups) == 0:
        return users
    users = [event_user.user for event_user in people_signups]
    return users


@event_router.get(
    "/event-signups/random/{event_id}",
    dependencies=[Permission.require("manage", "Event")],
    response_model=list[UserRead],
)
def get_random_event_signup(event_id: int, db: DB_dependency):
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


@event_router.patch(
    "/event-confirm-event-users/{event_id}",
    dependencies=[Permission.require("manage", "Event")],
    response_model=EventRead,
)
def confirm_event_users(db: DB_dependency, event_id: int, confirmed_users: list[UserRead]):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()

    if not event:
        raise HTTPException(404, detail="Event not found")

    if len(confirmed_users) > event.max_event_users:
        raise HTTPException(400, detail="Too many users for chosen event")

    confirmed_user_ids = [user.id for user in confirmed_users]

    for event_user in event.event_users:
        if event_user.user_id in confirmed_user_ids:
            event_user.confirmed_status = "confirmed"

    db.commit()
    db.refresh(event)

    return event


@event_router.post("/add-tag", dependencies=[Permission.require("manage", "Event")], response_model=AddEventTag)
def add_tag_to_event(data: AddEventTag, db: DB_dependency):

    newEventTag = EventTag_DB(tag_id=data.tag_id, event_id=data.event_id)

    try:
        db.add(newEventTag)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, detail="Invalid tag id or event id")

    return newEventTag


@event_router.get("/get-event-tags/{event_id}", response_model=list[EventTagRead])
def get_event_tags(db: DB_dependency, event_id: int):
    event = db.query(Event_DB).filter(Event_DB.id == event_id).one_or_none()

    if not event:
        raise HTTPException(404, detail="Event not found")

    event_tags = event.event_tags

    return event_tags


@event_router.get("/get-event-csv/{event_id}", dependencies=[Permission.require("manage", "Event")])
def get_event_csv(db: DB_dependency, event_id: int):
    event = db.query(Event_DB).filter(Event_DB.id == event_id).one_or_none()

    if not event:
        raise HTTPException(404, detail="Event not found")

    event_users = event.event_users
    event_users.sort(key=lambda e_user: e_user.user.last_name)

    # Down the line, this should also include email address, food preference and other important information about event signups.
    names: list[str] = []
    stil_ids: list[str] = []
    telephone_numbers: list[str] = []

    for event_user in event_users:
        user = event_user.user
        names.append(f"{user.first_name} {user.last_name}")
        if user.stil_id is None:
            stil_ids.append("")
        else:
            stil_ids.append(user.stil_id)
        telephone_numbers.append(user.telephone_number)

    d = {"Name": names, "Stil-id": stil_ids, "Telephone number": telephone_numbers}

    df = pd.DataFrame(data=d)
    csv_file = StringIO()
    df.to_csv(csv_file, index=False)
    response = StreamingResponse(iter([csv_file.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=event.csv"
    return response
