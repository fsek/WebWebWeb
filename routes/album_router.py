from fastapi import APIRouter
from database import DB_dependency
from api_schemas.album_schema import albumCreate
from db_models.album_model import Album_DB
from user.permission import Permission

album_router = APIRouter()


@album_router.post("/", dependencies=[Permission.require("manage", "Gallery")], response_model=dict[str, str])
def add_album(db: DB_dependency, album: albumCreate):
    new_album = Album_DB(name=album.name)
    db.add(new_album)
    db.commit

    return {"message": "Album successfully created"}
