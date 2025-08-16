from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Response
from database import DB_dependency
from db_models.document_model import Document_DB
from api_schemas.document_schema import DocumentRead, DocumentCreate, DocumentUpdate, document_create_form
from db_models.user_model import User_DB
from helpers.constants import MAX_DOC_TITLE
from helpers.pdf_checker import validate_pdf_header
from user.permission import Permission
from fastapi import File, UploadFile, HTTPException
import os
from fastapi.responses import FileResponse
from helpers.db_util import sanitize_title
from sqlalchemy.exc import IntegrityError

from pathlib import Path

document_router = APIRouter()

base_path = os.getenv("DOCUMENT_BASE_PATH")


@document_router.get("/", response_model=list[DocumentRead])
def get_all_documents(db: DB_dependency, manage_permission: Annotated[bool, Permission.check("manage", "Document")]):
    if manage_permission:
        documents = db.query(Document_DB).all()
    else:
        documents = db.query(Document_DB).filter(Document_DB.is_private == False).all()
    return documents


@document_router.post("/", dependencies=[Permission.require("manage", "Document")], response_model=DocumentRead)
async def upload_document(
    db: DB_dependency,
    uploader: Annotated[User_DB, Permission.member()],
    data: DocumentCreate = Depends(document_create_form),
    file: UploadFile = File(),
):
    await validate_pdf_header(file)

    if file.filename is None:
        raise HTTPException(400, detail="The file has no name")

    filename, ext = os.path.splitext(str(file.filename))

    sanitized_filename = sanitize_title(filename)

    if len(sanitized_filename) > MAX_DOC_TITLE:
        raise HTTPException(400, detail="The file name is too long")

    allowed_exts = {".pdf"}

    ext = ext.lower()

    if ext not in allowed_exts:
        raise HTTPException(400, "File extension not allowed")

    file.filename = f"{sanitized_filename}{ext}"

    file_path = Path(f"{base_path}/{sanitized_filename}{ext}")
    if file_path.is_file():
        raise HTTPException(409, detail="Filename is equal to already existing file")

    document = Document_DB(
        title=data.title,
        category=data.category,
        is_private=data.is_private,
        file_name=f"{sanitized_filename}{ext}",
        author_id=uploader.id,
    )

    try:
        db.add(document)
        db.commit()
        file_path.write_bytes(file.file.read())
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, detail="Something is invalid")

    return document


@document_router.get("/document_data/{document_id}", response_model=DocumentRead)
def get_document_data_by_id(
    document_id: int, db: DB_dependency, manage_permission: Annotated[bool, Permission.check("manage", "Document")]
):
    document = db.query(Document_DB).filter(Document_DB.id == document_id).one_or_none()
    if document is None:
        raise HTTPException(404, detail="Document not found")

    if document.is_private and not manage_permission:
        raise HTTPException(401, detail="Document is private, check your permissions m8")

    return document


@document_router.get("/document_file/{document_id}")
def get_document_file_by_id(
    document_id: int, db: DB_dependency, manage_permission: Annotated[bool, Permission.check("manage", "Document")]
):
    document = db.query(Document_DB).filter(Document_DB.id == document_id).one_or_none()
    if document is None:
        raise HTTPException(404, detail="Document not found")

    if document.is_private and not manage_permission:
        raise HTTPException(401, detail="Document is private, check your permissions m8")

    file_path = Path(f"{base_path}/{document.file_name}")
    if not file_path.exists():
        raise HTTPException(418, detail="Something is very cooked, contact the Webmasters pls!")

    return FileResponse(file_path, filename=document.file_name, media_type="application/octet-stream")


@document_router.get("/{document_id}")
def get_document_file(
    document_id: int,
    db: DB_dependency,
    manage_permission: Annotated[bool, Permission.check("manage", "Document")],
    response: Response,
):
    document = db.query(Document_DB).filter(Document_DB.id == document_id).one_or_none()
    if document is None:
        raise HTTPException(404, detail="Document not found")

    if document.is_private and not manage_permission:
        raise HTTPException(401, detail="Document is private, check your permissions m8")

    file_path = Path(f"/internal/document{base_path}/{document.file_name}")
    if not file_path.exists():
        raise HTTPException(418, detail="Something is very cooked, contact the Webmasters pls!")

    response.headers["X-Accel-Redirect"] = str(file_path)

    return response


@document_router.delete(
    "/delete_document/{document_id}",
    response_model=DocumentRead,
    dependencies=[Permission.require("manage", "Document")],
)
def delete_document(document_id: int, db: DB_dependency):
    document = db.query(Document_DB).filter(Document_DB.id == document_id).one_or_none()
    if document is None:
        raise HTTPException(404, detail="Document not found")

    try:
        db.delete(document)
        db.commit()
    except IntegrityError:
        raise HTTPException(500, detail="Something went wrong trying to delete the document, contact the Webmasters")

    os.remove(f"{base_path}/{document.file_name}")

    return document


@document_router.patch(
    "patch_document/{document_id}", response_model=DocumentRead, dependencies=[Permission.require("manage", "Document")]
)
def update_document(document_id: int, db: DB_dependency, data: DocumentUpdate):
    document = db.query(Document_DB).filter(Document_DB.id == document_id).one_or_none()
    if document is None:
        raise HTTPException(404, detail="Document not found")

    for var, value in vars(data).items():
        setattr(document, var, value) if value is not None else None

    db.commit()
    db.refresh(document)
    return document
