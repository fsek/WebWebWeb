from sqlalchemy.orm import Session
from typing import Union
from fastapi import APIRouter, HTTPException, status
from api_schemas.song_schemas import SongCreate, SongRead
from api_schemas.tag_schema import NollningTagRead, TagCreate, TagRead
from database import DB_dependency
from db_models.event_model import Event_DB
from db_models.event_tag_DB import EventTag_DB
from db_models.nollning_model import Nollning_DB
from db_models.nollning_tag_model import NollningTag_DB
from db_models.song_model import Song_DB
from db_models.tag_model import Tag_DB
from helpers.types import TAG_TYPE
from user.permission import Permission
from sqlalchemy.exc import IntegrityError


def create_nollning_tag(db: Session, data: TagCreate):
    nollning = db.query(Nollning_DB).filter(Nollning_DB.id == data.target_id).one_or_none()

    if not nollning:
        raise HTTPException(404, detail="Nollning not found")

    tag = db.query(Tag_DB).filter(Tag_DB.tag_type == data.tag_type).one_or_none()

    if not tag:
        raise HTTPException(404, detail="Tag not found")

    newtag = NollningTag_DB(name=data.name, nollning=nollning, nollning_id=data.target_id, tag=tag, tag_id=tag.id)

    try:
        db.add(newtag)
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(400, detail="Tag name not unique")

    return newtag


def create_event_tag(db: Session, data: TagCreate):
    event = db.query(Event_DB).filter(Event_DB.id == data.target_id).one_or_none()

    if not event:
        raise HTTPException(404, detail="Event not found")

    tag = db.query(Tag_DB).filter(Tag_DB.tag_type == data.tag_type).one_or_none()

    if not tag:
        raise HTTPException(404, detail="Tag not found")

    newtag = EventTag_DB(name=data.name, event=event, event_id=data.target_id, tag=tag, tag_id=tag.id)

    try:
        db.add(newtag)
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(400, detail="Tag name not unique")

    return newtag


def create_image_tag(db: Session, data: TagCreate):
    return


def create_cafe_tag(db: Session, data: TagCreate):
    return


def create_news_tag(db: Session, data: TagCreate):
    return
