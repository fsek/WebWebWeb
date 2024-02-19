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
from services.img_service import upload_img

img_router = APIRouter()

"""
@img_router.get("/")
def get_all_imgs(db: DB_dependency):
    imgs = db.query(Img_DB).all
    return imgs
    """


@img_router.post("/")
def upload(db: DB_dependency, file: UploadFile = File()):
    return upload_img(db, file)


@img_router.get("/{path}")
def get_img(path: str, db: DB_dependency):
    return FileResponse(f"/{path}")
