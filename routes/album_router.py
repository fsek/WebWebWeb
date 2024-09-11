from fastapi import APIRouter
from database import DB_dependency
from api_schemas.album_schema import AlbumCreate, AlbumRead
from db_models.album_model import Album_DB
from services.album_service import add_album, get_album, get_all_albums, delete_album
from user.permission import Permission

album_router = APIRouter()


@album_router.post("/", dependencies=[Permission.require("manage", "Gallery")], response_model=dict[str, str])
def create_album(db: DB_dependency, album: AlbumCreate):
    return add_album(db, album)


@album_router.get("/all", dependencies=[Permission.member()], response_model=list[AlbumRead])
def get_albums(db: DB_dependency):
    return get_all_albums(db)


@album_router.get("/", dependencies=[Permission.member()], response_model=AlbumRead)
def get_one_album(db: DB_dependency, id: int):
    return get_album(db, id)


@album_router.delete(
    "/{album_id}", dependencies=[Permission.require("manage", "Gallery")], response_model=dict[str, str]
)
def delete_one_album(db: DB_dependency, id: int):
    return delete_album(db, id)
