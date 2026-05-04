from typing import Annotated
from fastapi import Form
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_COURSE_DOC_AUTHOR, MAX_COURSE_DOC_SUB_CATEGORY, MAX_DOC_FILE_NAME, MAX_DOC_TITLE
from helpers.types import COURSE_DOCUMENT_CATEGORIES, datetime_utc


class CourseDocumentRead(BaseSchema):
    course_document_id: int
    title: str
    file_name: str
    course_id: int
    created_course_code: str
    author: str
    category: COURSE_DOCUMENT_CATEGORIES
    sub_category: str | None
    created_at: datetime_utc
    updated_at: datetime_utc


class CourseDocumentCreate(BaseSchema):
    title: Annotated[str, StringConstraints(max_length=MAX_DOC_TITLE)]
    course_id: int
    author: Annotated[str, StringConstraints(max_length=MAX_COURSE_DOC_AUTHOR)]
    category: COURSE_DOCUMENT_CATEGORIES = "Other"
    sub_category: Annotated[str, StringConstraints(max_length=MAX_COURSE_DOC_SUB_CATEGORY)] | None = None


# Apparently I have to do this to be able to send JSON forms at the same time as files in the POST course document router
def course_document_create_form(
    title: str = Form(...),
    course_id: int = Form(...),
    author: str = Form(...),
    category: COURSE_DOCUMENT_CATEGORIES = Form("Other"),
    sub_category: str | None = Form(None),
) -> CourseDocumentCreate:
    return CourseDocumentCreate(
        title=title,
        course_id=course_id,
        author=author,
        category=category,
        sub_category=sub_category,
    )


class CourseDocumentUpdate(BaseSchema):
    title: Annotated[str, StringConstraints(max_length=MAX_DOC_TITLE)]
    author: Annotated[str, StringConstraints(max_length=MAX_COURSE_DOC_AUTHOR)]
    category: COURSE_DOCUMENT_CATEGORIES = "Other"
    sub_category: Annotated[str, StringConstraints(max_length=MAX_COURSE_DOC_SUB_CATEGORY)] | None = None
