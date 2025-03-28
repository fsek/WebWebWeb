from fastapi import HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from db_models.documents_model import Documents_DB
from helpers.constants import MAX_DOCUMENT_TITLE
import random
import os


def upload_doc(db: Session, name: str, file: UploadFile = File()):
    if file.filename is None:
        raise HTTPException(400, detail="The file has no name")

    if len(file.filename) > MAX_DOCUMENT_TITLE:
        raise HTTPException(400, detail="The file name is too long")

    salt = random.getrandbits(24)
    file_path = Path(f"/{salt}{file.filename.replace(' ', '')}")
    if file_path.is_file():
        raise HTTPException(409, detail="Filename is equal to already existing file")

    file_path.write_bytes(file.file.read())
    doc = Documents_DB(file_path=file_path.name, name=name)
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


def get_single_img(db: Session, img_id: int):
    img = db.query(Img_DB).filter(Img_DB.id == img_id).one_or_none()

    if img == None:
        raise HTTPException(404, detail="File not found")

    return FileResponse(f"/{img.album.path}/{img.path}")
