from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from database import DB_dependency
from services.img_service import upload_img, remove_img, get_single_img
from user.permission import Permission

img_router = APIRouter()


@img_router.post("/", dependencies=[Permission.require("manage", "Gallery")], response_model=dict[str, str])
def upload(db: DB_dependency, album_id: int, file: UploadFile = File()):
    return upload_img(db, album_id, file)


@img_router.delete("/{id}", dependencies=[Permission.require("manage", "Gallery")], response_model=dict[str, str])
def delete(db: DB_dependency, id: int):
    return remove_img(db, id)


@img_router.get("/{id}")
def get_img(db: DB_dependency, id: int):
    return get_single_img(db, id)
