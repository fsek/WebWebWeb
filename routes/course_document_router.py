import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError

from api_schemas.course_document_schema import (
    CourseDocumentCreate,
    CourseDocumentRead,
    CourseDocumentUpdate,
    course_document_create_form,
)
from database import DB_dependency
from db_models.course_document_model import CourseDocument_DB
from db_models.course_model import Course_DB
from services.document_service import validate_file
from user.permission import Permission


course_document_router = APIRouter()


@course_document_router.get("/course/{course_id}", response_model=list[CourseDocumentRead])
def get_all_documents_from_course(course_id: int, db: DB_dependency):
    return db.query(CourseDocument_DB).filter_by(course_id=course_id).all()


@course_document_router.get("/{course_document_id}", response_model=CourseDocumentRead)
def get_course_document(course_document_id: int, db: DB_dependency):
    course_document = db.query(CourseDocument_DB).filter_by(course_document_id=course_document_id).one_or_none()
    if course_document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return course_document


@course_document_router.post(
    "/", response_model=CourseDocumentRead, dependencies=[Permission.require("manage", "Plugg")]
)
async def create_course_document(
    db: DB_dependency,
    data: CourseDocumentCreate = Depends(course_document_create_form),
    file: UploadFile = File(),
):
    course = db.query(Course_DB).filter_by(course_id=data.course_id).one_or_none()
    if course is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Course not found")

    base_path = os.getenv("COURSE_DOCUMENT_BASE_PATH")
    if base_path is None:
        raise HTTPException(500, detail="Document base path is not configured")

    sanitized_filename, ext, file_path = await validate_file(base_path, file)

    course_document = CourseDocument_DB(
        title=data.title,
        file_name=f"{sanitized_filename}{ext}",
        course_id=data.course_id,
        author=data.author,
        category=data.category,
        sub_category=data.sub_category,
    )

    try:
        db.add(course_document)
        db.commit()
        file_path.write_bytes(file.file.read())
        db.refresh(course_document)
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, detail="Something is invalid")

    return course_document


@course_document_router.patch(
    "/{course_document_id}",
    response_model=CourseDocumentRead,
    dependencies=[Permission.require("manage", "Plugg")],
)
def update_course_document(course_document_id: int, data: CourseDocumentUpdate, db: DB_dependency):
    course_document = db.query(CourseDocument_DB).filter_by(course_document_id=course_document_id).one_or_none()
    if course_document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    for var, value in vars(data).items():
        # Note that we always set None values, to clear fields if the user wants to.
        setattr(course_document, var, value)

    db.commit()
    db.refresh(course_document)
    return course_document


@course_document_router.get("/document_file/{course_document_id}")
def get_course_document_file_by_id(course_document_id: int, db: DB_dependency):
    base_path = os.getenv("COURSE_DOCUMENT_BASE_PATH")

    document = (
        db.query(CourseDocument_DB).filter(CourseDocument_DB.course_document_id == course_document_id).one_or_none()
    )
    if document is None:
        raise HTTPException(404, detail="Document not found")

    file_path = Path(f"{base_path}/{document.file_name}")
    if not file_path.exists():
        raise HTTPException(418, detail="Something is very cooked, contact the Webmasters pls!")

    return FileResponse(file_path, filename=document.file_name, media_type="application/octet-stream")


@course_document_router.get("/{course_document_id}")
def get_course_document_file(
    course_document_id: int,
    db: DB_dependency,
    response: Response,
):
    base_path = os.getenv("COURSE_DOCUMENT_BASE_PATH")

    document = (
        db.query(CourseDocument_DB).filter(CourseDocument_DB.course_document_id == course_document_id).one_or_none()
    )
    if document is None:
        raise HTTPException(404, detail="Document not found")

    file_path = Path(f"/internal/document{base_path}/{document.file_name}")
    if not file_path.exists():
        # This will always trigger if we are in local dev, don't worry about it
        # If we get this in production something is very wrong
        raise HTTPException(418, detail="Something is very cooked, contact the Webmasters pls!")

    response.headers["X-Accel-Redirect"] = str(file_path)

    # I got an error in swagger if these were not included
    response.status_code = 200
    response.body = b""
    return response


@course_document_router.delete(
    "/{course_document_id}",
    response_model=CourseDocumentRead,
    dependencies=[Permission.require("manage", "Plugg")],
)
def delete_course_document(course_document_id: int, db: DB_dependency):
    base_path = os.getenv("COURSE_DOCUMENT_BASE_PATH")
    course_document = db.query(CourseDocument_DB).filter_by(course_document_id=course_document_id).one_or_none()
    if course_document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    try:
        db.delete(course_document)
        db.commit()
        os.remove(f"{base_path}/{course_document.file_name}")
    except IntegrityError:
        db.rollback()
        raise HTTPException(500, detail="Something went wrong trying to delete the document, contact the Webmasters")
    return course_document
