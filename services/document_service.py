from fastapi import HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from db_models.documents_model import Documents_DB
from helpers.constants import MAX_DOCUMENT_TITLE, MAX_DOCUMENT_BYTES
import random
import os


def upload_doc(db: Session, name: str, user_id: int, file: UploadFile = File()):
    if file.filename is None:
        raise HTTPException(400, detail="The file has no name")

    if len(file.filename) > MAX_DOCUMENT_TITLE:
        raise HTTPException(400, detail="The file name is too long")

    salt = random.getrandbits(24)
    file_path = Path(f"/{salt}{file.filename.replace(' ', '-')}")
    if file_path.is_file():
        raise HTTPException(400, detail="Filename is equal to already existing file")
    if file.size == None or file.size > MAX_DOCUMENT_BYTES:
        raise HTTPException(400, detail="File size is bigger than limit of 50 MB")

    file_path.write_bytes(file.file.read())
    doc = Documents_DB(file_path=file_path.name, name=name, file_type="pdf", uploader_id=user_id)
    db.add(doc)
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
