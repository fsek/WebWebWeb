from fastapi import APIRouter, UploadFile, File
from database import DB_dependency
from services.img_service import upload_img, remove_img, get_single_img
from user.permission import Permission

img_router = APIRouter()


@img_router.post("/", dependencies=[Permission.require("manage", "Gallery")], response_model=dict[str, str])
def upload_image(db: DB_dependency, album_id: int, file: UploadFile = File()):
    return upload_img(db, album_id, file)


@img_router.delete("/{id}", dependencies=[Permission.require("manage", "Gallery")], response_model=dict[str, str])
def delete_image(db: DB_dependency, id: int):
    return remove_img(db, id)


@img_router.get("/stream/{img_id}", dependencies=[Permission.member()])
def get_image(db: DB_dependency, img_id: int):
    return get_single_img(db, img_id)
