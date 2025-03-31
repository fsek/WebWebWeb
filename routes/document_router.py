from pydoc import doc
from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func
from database import DB_dependency
from db_models.document_model import Document_DB
from api_schemas.document_schema import DocumentRead, DocumentCreate, DocumentUpdate
from db_models.user_model import User_DB
from helpers.constants import MAX_DOC_TITLE
from user.permission import Permission
from fastapi import File, UploadFile, HTTPException
import random
import os

from pathlib import Path

document_router = APIRouter()


@document_router.get("/", response_model=list[DocumentRead])
def get_all_documents(db: DB_dependency):
    documents = db.query(Document_DB).all()
    return documents


@document_router.post("/", dependencies=[Permission.require("manage", "Document")], response_model=dict[str, str])
def upload_document(data: Annotated[User_DB, Permission().member()], db: DB_dependency, file: UploadFile = File()):
    if file.filename is None:
        raise HTTPException(400, detail="The file has no name")

    if len(file.filename) > MAX_DOC_TITLE:
        raise HTTPException(400, detail="The file name is too long")

    salt = random.getrandbits(24)
    file_path = Path(f"/{salt}{file.filename.replace(' ', '')}")
    if file_path.is_file():
        raise HTTPException(400, detail="Filename is equal to already existing file")

    file_path.write_bytes(file.file.read())
    doc = Document_DB(title=file_path.name, user_id=data.id, path=file_path.name)
    db.add(doc)
    db.commit()
    return {"message": "File saved successfully"}
