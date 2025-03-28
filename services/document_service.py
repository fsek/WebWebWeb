from fastapi import HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from db_models.documents_model import Documents_DB
from helpers.constants import MAX_DOCUMENT_TITLE, MAX_DOCUMENT_BYTES
import random
import os
from datetime import datetime, timezone


def upload_doc(db: Session, name: str, user_id: int, file: UploadFile = File()):
    if file.filename is None:
        raise HTTPException(400, detail="The file has no name")

    if len(name) > MAX_DOCUMENT_TITLE:
        raise HTTPException(400, detail="The file name is too long")

    file_path = Path(f"documents/{datetime.date}-{name.replace(' ', '-')}.pdf")
    if file_path.is_file():
        raise HTTPException(400, detail="Filename is equal to already existing file")
    if file.size == None or file.size > MAX_DOCUMENT_BYTES:
        raise HTTPException(400, detail="File size is bigger than limit of 50 MB")

    file_path.write_bytes(file.file.read())  # TODO correct file type
    doc = Documents_DB(file_path=file_path.name, name=name, file_type="pdf", uploader_id=user_id)
    db.add(doc)
    db.commit()
    return doc


def remove_doc(db: Session, img_id: int):
    # img = db.query(Img_DB).filter(Img_DB.id == img_id).one_or_none()

    # if img == None:
    #     raise HTTPException(404, detail="File not found")

    # os.remove(f"/{img.album.path}/{img.path}")
    # db.delete(img)
    # db.commit()

    # return {"message": "File removed successfully"}
    pass


def get_single_doc(db: Session, doc_id: int):
    doc = db.query(Documents_DB).filter(Documents_DB.id == doc_id).one_or_none()

    if doc == None:
        raise HTTPException(404, detail="File not found")

    return FileResponse(f"/{doc.file_path}")
    pass
