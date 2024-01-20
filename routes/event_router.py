from fastapi import APIRouter
from database import DB_dependency
from db_models.event_model import Event_DB
from api_schemas.event_schemas import EventCreate, EventRead
from services.event_service import create_new_event, delete_event
from user.permission import Permission

event_router = APIRouter()


@event_router.get("/", response_model=list[EventRead])
def get_all_events(db: DB_dependency):
    events = db.query(Event_DB).all()
    return events


# perhaps only be able to create events for your own council?
@event_router.post("/", dependencies=[Permission.require("manage", "Event")])
def create_event(data: EventCreate, db: DB_dependency):
    event = create_new_event(data, db)
    return event


@event_router.delete("/{event_id}", dependencies=[Permission.require("manage", "Event")])
def remove(event_id: int, db: DB_dependency):
    delete_event(event_id, db)
    return
