from fastapi import APIRouter
from database import DB_dependency
from api_schemas.album_schema import AlbumCreate, AlbumRead
from services.album_service import add_album, get_album, get_all_albums, delete_album, delete_year
from user.permission import Permission

album_router = APIRouter()


@album_router.post("/", dependencies=[Permission.require("manage", "Gallery")], response_model=AlbumRead)
def create_album(db: DB_dependency, album: AlbumCreate):
    return add_album(db, album)


@album_router.get("/all", dependencies=[Permission.member()], response_model=list[AlbumRead])
def get_albums(db: DB_dependency):
    return get_all_albums(db)


@album_router.get("/{album_id}", dependencies=[Permission.member()], response_model=AlbumRead)
def get_one_album(db: DB_dependency, album_id: int):
    return get_album(db, album_id)


@album_router.delete(
    "/year/{year}", dependencies=[Permission.require("manage", "Gallery")], response_model=dict[str, str]
)
def delete_one_album(db: DB_dependency, album_id: int):
    return delete_album(db, album_id)
