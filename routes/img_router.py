from fastapi import APIRouter, UploadFile, File
from database import DB_dependency
from fastapi.responses import FileResponse
from services.img_service import upload_img
from user.permission import Permission

img_router = APIRouter()

"""
@img_router.get("/")
def get_all_imgs(db: DB_dependency):
    imgs = db.query(Img_DB).all
    return imgs
    """


@img_router.post("/", dependencies=[Permission.require("manage", "Gallery")], response_model=dict[str, str])
def upload(db: DB_dependency, file: UploadFile = File()):
    return upload_img(db, file)


# Vet inte om denna behövs
# @img_router.get("/{path}", dependencies=[Permission.require("view", "Gallery")])
# def get_img(path: str, db: DB_dependency):
#    return FileResponse(f"/{path}")
