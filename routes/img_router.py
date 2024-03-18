from fastapi import APIRouter, UploadFile, File
from database import DB_dependency
from fastapi.responses import FileResponse
from services.img_service import upload_img
from user.permission import Permission

img_router = APIRouter()

@img_router.post("/", dependencies=[Permission.require("manage", "Gallery")], response_model=dict[str, str])
def upload(db: DB_dependency, album_id: int, file: UploadFile = File()):
    return upload_img(db, album_id, file)



