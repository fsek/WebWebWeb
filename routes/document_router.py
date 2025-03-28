from pydoc import doc
from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func
from database import DB_dependency
from db_models.document_model import Document_DB
from api_schemas.document_schema import DocumentRead, DocumentCreate, DocumentUpdate
from db_models.user_model import User_DB
from helpers.constants import MAX_DOC_TITLE
from routes import ad_router
from user.permission import Permission
from fastapi import File, UploadFile, HTTPException
import random
from pathlib import Path

document_router = APIRouter()


@document_router.get("/", response_model=list[DocumentRead])
def get_all_documents(db: DB_dependency):
    documents = db.query(Document_DB).all()
    return documents


@document_router.get("/{id}", response_model=DocumentRead)
def get_document_by_id(id: int, db: DB_dependency):
    document = db.query(Document_DB).filter_by(document_id_id=id).one_or_none()
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return document


@document_router.get("/title/{stitle}", response_model=list[DocumentRead])
def get_document_by_title(stitle: str, db: DB_dependency):
    documents = db.query(Document_DB).filter(func.lower(Document_DB.title) == func.lower(stitle)).all()
    if len(documents) == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
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
    doc = Document_DB(title=file_path.name, user_id=data.id)
    db.add(doc)
    db.commit()
    return {"message": "File saved successfully"}
