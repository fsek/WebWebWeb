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
from fastapi.responses import FileResponse


from pathlib import Path

document_router = APIRouter()

UPLOAD_DIR = Path("document_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


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
    filename = f"{salt}{file.filename.replace(' ', '')}"
    file_path = UPLOAD_DIR / filename

    if file_path.is_file():
        raise HTTPException(400, detail="Filename is equal to already existing file")

    file_path.write_bytes(file.file.read())
    doc = Document_DB(title=file.filename, path=str(filename), salt=salt)
    db.add(doc)
    db.commit()
    return {"message": "File saved successfully"}


@document_router.get("/{document_id}", response_model=DocumentRead)
def get_document_by_id(document_id: int, db: DB_dependency):
    document = db.query(Document_DB).filter(Document_DB.document_id == document_id).one_or_none()
    if document is None:
        raise HTTPException(404, detail="Document not found")

    file_path = UPLOAD_DIR / document.path

    if not file_path.exists():
        available_files = "\n".join(os.listdir(UPLOAD_DIR))
        raise HTTPException(
            status_code=404,
            detail={
                "message": "File not found",
                "expected_path": str(file_path),
                "available_files": available_files,
                "stored_filename": document.path,
            },
        )

    return FileResponse(file_path, filename=document.title, media_type="application/octet-stream")
