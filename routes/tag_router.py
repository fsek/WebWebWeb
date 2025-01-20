from typing import Union
from fastapi import APIRouter, HTTPException, status
from api_schemas.song_schemas import SongCreate, SongRead
from api_schemas.tag_schema import EventTagRead, NollningTagRead, TagCreate, TagRead
from database import DB_dependency
from db_models.nollning_model import Nollning_DB
from db_models.nollning_tag_model import NollningTag_DB
from db_models.song_model import Song_DB
from db_models.tag_model import Tag_DB
from helpers.types import TAG_TYPE
from services.tag_service import create_event_tag, create_nollning_tag
from user.permission import Permission
from sqlalchemy.exc import IntegrityError

tag_router = APIRouter()


@tag_router.get("/tag_types", response_model=list[TagRead])
def get_tag_types(db: DB_dependency):
    tags = db.query(Tag_DB).all()

    return tags


# @tag_router.get("/", response_model=list[Union[NollningTagRead]])
# def get_tags(db: DB_dependency, data: Union[TAG_TYPE, None] = None):


@tag_router.post("/", response_model=Union[NollningTagRead, EventTagRead])
def post_tag(db: DB_dependency, data: TagCreate):
    if data.tag_type == "Nollning":
        newtag = create_nollning_tag(db, data)

        return newtag

    if data.tag_type == "Event":
        newtag = create_event_tag(db, data)

        return newtag

    return
