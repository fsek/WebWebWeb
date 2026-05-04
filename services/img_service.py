from fastapi import HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from db_models.album_model import Album_DB
from db_models.img_model import Img_DB
from helpers.constants import MAX_IMG_NAME
import random
import os
from helpers.db_util import sanitize_title
from sqlalchemy.exc import IntegrityError


def upload_img(db: Session, album_id: int, file: UploadFile = File()):
    base_path = os.getenv("ALBUM_BASE_PATH")
    if base_path is None:
        raise HTTPException(500, detail="Server configuration error: ALBUM_BASE_PATH not set")

    if file.filename is None:
        raise HTTPException(400, detail="The file has no name")

    if len(file.filename) > MAX_IMG_NAME:
        raise HTTPException(400, detail="The file name is too long")

    album = db.query(Album_DB).filter(Album_DB.id == album_id).one_or_none()
    if album == None:
        raise HTTPException(404, detail="Album not found")

    salt = random.getrandbits(24)

    name, ext = os.path.splitext(file.filename)

    sanitized_filename = sanitize_title(name)

    allowed_exts = {".png", ".jpg", ".jpeg", ".gif"}

    ext = ext.lower()

    if ext not in allowed_exts:
        raise HTTPException(400, "file extension not allowed")

    BASE_UPLOAD_DIR = Path(f"{base_path}")

    album_dir = (BASE_UPLOAD_DIR / album.path).resolve()

    if not str(album_dir).startswith(str(BASE_UPLOAD_DIR)):
        raise HTTPException(400, "Invalid album path")

    file.filename = sanitized_filename

    file_path = Path(f"{album.path}/{salt}{sanitized_filename}{ext}")
    if file_path.is_file():
        raise HTTPException(409, detail="Filename is equal to already existing file")

    img = Img_DB(path=str(file_path), album_id=album_id)

    try:
        db.add(img)
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, detail="Error creating image in the database")

    try:
        file_path.write_bytes(file.file.read())
    except OSError:
        db.rollback()
        raise HTTPException(500, detail="Error saving image to disk")

    db.commit()

    return {"message": "File saved successfully"}


def remove_img(db: Session, img_id: int):
    img = db.query(Img_DB).filter(Img_DB.id == img_id).one_or_none()

    if img == None:
        raise HTTPException(404, detail="File not found")

    try:
        path = Path(img.path)
        path.unlink(missing_ok=True)
    except OSError:
        raise HTTPException(500, detail="Error deleting file")

    db.delete(img)
    db.commit()

    return {"message": "File removed successfully"}


def get_single_img(db: Session, img_id: int):
    img = db.query(Img_DB).filter(Img_DB.id == img_id).one_or_none()

    if img == None:
        raise HTTPException(404, detail="File not found")

    return FileResponse(img.path)
