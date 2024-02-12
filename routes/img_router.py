from curses.ascii import HT
from email import message
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from database import DB_dependency, get_db
from db_models.img_model import Img_DB
from db_models.permission_model import Permission_DB
from db_models.post_model import Post_DB
from api_schemas.permission_schemas import (
    PermissionCreate,
    PermissionRead,
    UpdatePermission,
)
from services.permission_service import assign_permission, unassign_permission
from user.permission import Permission
from PIL import Image
from fastapi.responses import FileResponse
import os.path
from pathlib import Path

img_router = APIRouter()

"""
@img_router.get("/")
def get_all_imgs(db: DB_dependency):
    imgs = db.query(Img_DB).all
    return imgs
    """


@img_router.post("/")
def upload_img(db: DB_dependency, file: UploadFile = File()):
    # This will be moved to services later
    try:
        file_path = Path(f"/path_to_put/{file.filename}")
        if file_path.is_file():
            raise HTTPException(404)

        file_path.write_bytes(file.file.read())
        img = Img_DB(path=file_path.name)
        db.add(img)
        db.commit
        return {"message": "File saved successfully"}

    except Exception as e:
        raise e
        return {"message": e.args}


@img_router.get("/{id}")
def get_img(id: str, db: DB_dependency):
    return FileResponse(f"/path_to_put/{id}")
