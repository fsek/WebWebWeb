from fastapi import APIRouter
from database import DB_dependency
from api_schemas.album_schema import AlbumCreate, AlbumPatch, AlbumPhotographerAdd, AlbumRead
from services.album_service import (
    add_album,
    edit_album,
    get_album,
    get_all_albums,
    delete_album,
    delete_year,
    add_photographer,
    remove_photographer,
)
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


@album_router.delete("/{album_id}", dependencies=[Permission.require("manage", "Gallery")], response_model=AlbumRead)
def delete_one_album(db: DB_dependency, album_id: int):
    return delete_album(db, album_id)


@album_router.delete(
    "/year/{year}", dependencies=[Permission.require("manage", "Gallery")], response_model=dict[str, str]
)
def delete_album_year(db: DB_dependency, year: int):
    return delete_year(db, year)


@album_router.patch("/{album_id}", dependencies=[Permission.require("manage", "Gallery")], response_model=AlbumRead)
def patch_album(db: DB_dependency, album_id: int, data: AlbumPatch):
    return edit_album(db, album_id, data)


@album_router.patch(
    "/add_photographer", dependencies=[Permission.require("manage", "Gallery")], response_model=AlbumRead
)
def add_album_photographer(db: DB_dependency, data: AlbumPhotographerAdd):
    return add_photographer(db, data.album_id, data.user_id)


@album_router.patch(
    "/remove_photographer", dependencies=[Permission.require("manage", "Gallery")], response_model=AlbumRead
)
def remove_album_photographer(db: DB_dependency, data: AlbumPhotographerAdd):
    return remove_photographer(db, data.album_id, data.user_id)
