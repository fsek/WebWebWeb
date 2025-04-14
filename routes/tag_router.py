from fastapi import APIRouter, HTTPException, status
from api_schemas.song_schemas import SongCreate, SongRead
from api_schemas.tag_schema import TagCreate, TagEdit, TagRead
from database import DB_dependency
from db_models.song_model import Song_DB
from db_models.tag_model import Tag_DB
from db_models.event_model import Event_DB
from db_models.event_tag_model import EventTag_DB
from user.permission import Permission
from sqlalchemy.exc import IntegrityError


tag_router = APIRouter()


@tag_router.post("/", response_model=TagRead, dependencies=[Permission.require("manage", "Tags")])
def post_tag(db: DB_dependency, data: TagCreate):
    newtag = Tag_DB(name=data.name)

    try:
        db.add(newtag)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, detail="Invalid tag name")

    return newtag


@tag_router.patch("/", response_model=TagRead, dependencies=[Permission.require("manage", "Tags")])
def edit_tag(db: DB_dependency, data: TagEdit):
    tag = db.query(Tag_DB).get(data.id)

    if tag is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    tag.name = data.name

    db.commit()
    return tag


@tag_router.get("/", response_model=list[TagRead])
def get_tags(db: DB_dependency):
    tags = db.query(Tag_DB).all()

    return tags


@tag_router.delete("/{tag_id}", response_model=TagRead, dependencies=[Permission.require("manage", "Tags")])
def delete_tag(db: DB_dependency, tag_id: int):
    tag = db.query(Tag_DB).filter(Tag_DB.id == tag_id).one_or_none()
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(tag)
    db.commit()
    return tag
