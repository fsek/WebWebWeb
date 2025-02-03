from fastapi import APIRouter, HTTPException, status
from api_schemas.song_schemas import SongCreate, SongRead
from api_schemas.tag_schema import TagCreate, TagRead
from database import DB_dependency
from db_models.song_model import Song_DB
from db_models.tag_model import Tag_DB
from user.permission import Permission
from sqlalchemy.exc import IntegrityError


tag_router = APIRouter()


@tag_router.post("/", response_model=TagRead)
def post_tag(db: DB_dependency, data: TagCreate):
    newtag = Tag_DB(name=data.name)

    try:
        db.add(newtag)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, detail="Invalid tag name")

    return newtag


@tag_router.get("/", response_model=list[TagRead])
def get_tags(db: DB_dependency):
    tags = db.query(Tag_DB).all()

    return tags
