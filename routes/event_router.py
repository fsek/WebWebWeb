from datetime import datetime
from io import StringIO
import os
from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from psycopg import IntegrityError
from api_schemas.event_signup_schemas import EventSignupRead
from api_schemas.tag_schema import EventTagRead
from database import DB_dependency
from db_models.event_model import Event_DB
from api_schemas.event_schemas import AddEventTag, EventCreate, EventRead, EventUpdate
from db_models.event_user_model import EventUser_DB
from db_models.user_model import User_DB
from db_models.event_tag_model import EventTag_DB
from helpers.image_checker import validate_image
from db_models.post_model import Post_DB
from services.event_service import create_new_event, delete_event, update_event
from user.permission import Permission
import random
from helpers.types import ALLOWED_EXT, ALLOWED_IMG_SIZES, ALLOWED_IMG_TYPES, ASSETS_BASE_PATH
from pathlib import Path


import pandas as pd

event_router = APIRouter()


@event_router.get("/", response_model=list[EventRead])
def get_all_events(db: DB_dependency):
    events = db.query(Event_DB).all()
    return events


@event_router.get("/priorities", response_model=list[str])
def get_event_priorities(db: DB_dependency):

    posts = db.query(Post_DB).all()

    priorities: set[str] = set()

    for post in posts:
        priorities.add(post.name_sv)

    priorities.add("Fadder")

    priorities.add("Nolla")

    return list(priorities)


@event_router.patch("/confirmed/{event_id}", response_model=EventRead)
def confirm_places(
    db: DB_dependency,
    event_id: int,
):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()
    if not event:
        raise HTTPException(404, detail="Event not found")
    if event.event_users_confirmed:
        raise HTTPException(400, detail="Event users already confirmed")

    event.event_users_confirmed = True

    db.commit()
    db.refresh(event)

    return event


@event_router.get("/{eventId}", response_model=EventRead)
def get_single_event(db: DB_dependency, eventId: int):
    event = db.query(Event_DB).filter(Event_DB.id == eventId).one_or_none()

    if not event:
        raise HTTPException(404, detail="Event not found")

    return event


@event_router.post("/{event_id}/image", dependencies=[Permission.require("manage", "Event")])
async def post_event_image(event_id: int, db: DB_dependency, image: UploadFile = File()):
    event = db.query(Event_DB).get(event_id)
    if not event:
        raise HTTPException(404, "No event found")

    if image:

        await validate_image(image)

        filename: str = str(image.filename)
        _, ext = os.path.splitext(filename)

        ext = ext.lower()

        if ext not in ALLOWED_EXT:
            raise HTTPException(400, "file extension not allowed")

        dest_path = Path(f"{ASSETS_BASE_PATH}/events/{event.id}{ext}")

        dest_path.write_bytes(image.file.read())


@event_router.get("/{event_id}/image/{size}", dependencies=[Permission.require("manage", "Event")])
def get_event_image(event_id: int, size: ALLOWED_IMG_TYPES, db: DB_dependency):

    dims = ALLOWED_IMG_SIZES[size]

    event = db.query(Event_DB).get(event_id)
    if not event:
        raise HTTPException(404, "No image for this event")

    asset_dir = Path(f"{ASSETS_BASE_PATH}") / "events"

    matches = list(asset_dir.glob(f"{event.id}.*"))
    if not matches:
        raise HTTPException(404, "Image not found")

    filename = matches[0].name

    internal = f"/internal/{dims}{ASSETS_BASE_PATH}/events/{filename}"

    return Response(status_code=200, headers={"X-Accel-Redirect": internal})


@event_router.get("/{event_id}/image/stream", dependencies=[Permission.require("manage", "Event")])
def get_event_image_stream(event_id: int, db: DB_dependency):
    event = db.query(Event_DB).get(event_id)
    if not event:
        raise HTTPException(404, "No image for this event")

    asset_dir = Path(f"{ASSETS_BASE_PATH}") / "events"

    matches = list(asset_dir.glob(f"{event.id}.*"))
    if not matches:
        raise HTTPException(404, "Image not found")

    filename = matches[0].name

    internal = f"/{ASSETS_BASE_PATH}/events/{filename}"

    return FileResponse(internal)


@event_router.post("/", dependencies=[Permission.require("manage", "Event")], response_model=EventRead)
def create_event(
    data: EventCreate,
    db: DB_dependency,
):
    event = create_new_event(data, db)
    return event


@event_router.delete("/{event_id}", dependencies=[Permission.require("manage", "Event")], response_model=EventRead)
def event_remove(event_id: int, db: DB_dependency):
    return delete_event(event_id, db)


@event_router.patch("/{event_id}", dependencies=[Permission.require("manage", "Event")], response_model=EventRead)
def event_update(
    event_id: int,
    data: EventUpdate,
    db: DB_dependency,
):
    event = update_event(event_id, data, db)
    return event


@event_router.get(
    "/event-signups/all/{event_id}",
    dependencies=[Permission.require("manage", "Event")],
    response_model=list[EventSignupRead],
)
def get_all_event_signups(event_id: int, db: DB_dependency):
    people_signups = db.query(EventUser_DB).filter_by(event_id=event_id).all()
    empty: list[EventUser_DB] = []
    if len(people_signups) == 0:
        return empty
    return people_signups


@event_router.get(
    "/event-signups/{event_id}",
    dependencies=[Permission.require("manage", "Event")],
    response_model=list[EventSignupRead],
)
def create_event_signup_list(event_id: int, db: DB_dependency):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()
    if event is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No event exist")

    if event.signup_end > datetime.now():
        raise HTTPException(400, detail="Event signups are not closed yet")

    people_signups = db.query(EventUser_DB).filter_by(event_id=event_id).all()

    for event_user in people_signups:
        if event_user.confirmed_status:
            raise HTTPException(400, detail="Event signups are already confirmed")

    users: list[User_DB] = []
    if len(people_signups) == 0:
        return users
    if len(people_signups) <= event.max_event_users or event.max_event_users == 0:
        for event_user in people_signups:
            event_user.confirmed_status = True
        db.commit()
        return people_signups

    priorites: set[str] = set()

    prioritized_people: list[EventUser_DB] = []

    for priority in event.priorities:
        priorites.add(priority.priority)

    for person in people_signups:
        if person.priority in priorites:
            prioritized_people.append(person)

    places_left = event.max_event_users - len(prioritized_people)

    if event.lottery:
        # Random fill
        non_prioritized = [p for p in people_signups if p not in prioritized_people]
        random.seed(event_id)
        random.shuffle(non_prioritized)
        prioritized_people.extend(non_prioritized[:places_left])
    else:
        # FIFO fill
        non_prioritized = (
            db.query(EventUser_DB).filter_by(event_id=event_id).order_by(EventUser_DB.created_at.asc()).all()
        )
        non_prioritized = [p for p in non_prioritized if p not in prioritized_people]
        prioritized_people.extend(non_prioritized[:places_left])

    for event_user in prioritized_people:
        event_user.confirmed_status = True

    db.commit()

    return prioritized_people


@event_router.patch(
    "/event-confirm-event-users/{event_id}",
    dependencies=[Permission.require("manage", "Event")],
    response_model=EventRead,
)
def confirm_event_users(db: DB_dependency, event_id: int, confirmed_users: list[int]):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()

    if not event:
        raise HTTPException(404, detail="Event not found")

    if event.max_event_users != 0 and len(confirmed_users) > event.max_event_users:
        raise HTTPException(400, detail="Too many users for chosen event")

    confirmed_user_ids = [id for id in confirmed_users]

    for event_user in event.event_users:
        if event_user.user_id in confirmed_user_ids:
            event_user.confirmed_status = True

    db.commit()
    db.refresh(event)

    return event


@event_router.patch(
    "/event-unconfirm-event-users/{event_id}",
    dependencies=[Permission.require("manage", "Event")],
    response_model=EventRead,
)
def unconfirm_event_users(db: DB_dependency, event_id: int, unconfirmed_users: list[int]):
    event = db.query(Event_DB).filter_by(id=event_id).one_or_none()

    if not event:
        raise HTTPException(404, detail="Event not found")

    unconfirmed_user_ids = [id for id in unconfirmed_users]

    for event_user in event.event_users:
        if event_user.user_id in unconfirmed_user_ids:
            event_user.confirmed_status = False

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
