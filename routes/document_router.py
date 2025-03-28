from pydoc import doc
from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func
from database import DB_dependency
from db_models.document_model import Document_DB
from api_schemas.document_schema import DocumentRead, DocumentCreate, DocumentUpdate
from db_models.user_model import User_DB
from routes import ad_router
from user.permission import Permission
from fastapi import File, UploadFile, HTTPException

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


@document_router.post("/uploadFile", response_model=DocumentRead)
async def upload_document(data: DocumentCreate, db: DB_dependency, file: UploadFile):
    document = db.query(Document_DB).filter_by(title=data.title).one_or_none()
    if document is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Document already exists")
    document = Document_DB(title=data.title, is_private=data.is_private, user_id=data.user_id, date=data.date, file = )
    db.add(document)
    db.commit()
    return file.filename
