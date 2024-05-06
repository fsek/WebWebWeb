from fastapi import HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
from db_models.album_model import Album_DB
from db_models.img_model import Img_DB
from helpers.constants import MAX_IMG_NAME
import random
import os


def upload_img(db: Session, album_id: int, file: UploadFile = File()):
    if file.filename is None:
        raise HTTPException(400, detail="The file has no name")

    if len(file.filename) > MAX_IMG_NAME:
        raise HTTPException(400, detail="The file name is too long")

    album = db.query(Album_DB).filter(Album_DB.id == album_id).one_or_none()
    if album == None:
        raise HTTPException(404, detail="Album not found")

    salt = random.getrandbits(24)
    file_path = Path(f"/{album.name}/{salt}{file.filename.replace(' ', '')}")
    if file_path.is_file():
        raise HTTPException(409, detail="Filename is equal to already existing file")

    file_path.write_bytes(file.file.read())
    img = Img_DB(path=file_path.name, album_id=album_id)
    db.add(img)
    db.commit()
    return {"message": "File saved successfully"}


def remove_img(db: Session, img_id: int):
    img = db.query(Img_DB).filter(Img_DB.id == img_id).one_or_none()

    if img == None:
        raise HTTPException(404, detail="File not found")

    os.remove(f"/{img.album.path}/{img.path}")
    db.delete(img)
    db.commit()

    return {"message": "File removed successfully"}
