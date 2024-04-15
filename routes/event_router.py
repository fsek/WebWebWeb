from fastapi import APIRouter, HTTPException, status
from database import DB_dependency
from db_models.event_model import Event_DB
from api_schemas.event_schemas import EventCreate, EventRead, EventUpdate
from api_schemas.user_schemas import UserRead
from db_models.event_user_model import EventUser_DB
from services.event_service import create_new_event, delete_event, update_event
from user.permission import Permission
import random

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

@event_router.get("/{event_id}", dependencies=[Permission.require("manage", "Event")], response_model=list[UserRead])
def getAllSignups(event_id: int, db: DB_dependency):
    people = db.query(EventUser_DB).filter_by(event_id = event_id).all()
    if len(people)==0:
        raise HTTPException(status.HTTP_204_NO_CONTENT, detail="No user has signed up to this event")
    return people

@event_router.get("/{event_id}", dependencies=[Permission.require("manage", "Event")], response_model=list[UserRead])
def getRandomSignup(event_id: int, db: DB_dependency):
    people = db.query(EventUser_DB).filter_by(event_id = event_id).all()
    if len(people)==0:
        raise HTTPException(status.HTTP_204_NO_CONTENT, detail="No user has signed up to this event")
    random.shuffle(people)
    return people
