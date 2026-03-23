from typing import Annotated
from fastapi import UploadFile
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_COURSE_DOC_AUTHOR, MAX_COURSE_DOC_SUB_CATEGORY, MAX_DOC_FILE_NAME, MAX_DOC_TITLE
from helpers.types import COURSE_DOCUMENT_CATEGORIES, datetime_utc


class CourseDocumentRead(BaseSchema):
    course_document_id: int
    title: str
    file_name: str
    course_id: int
    author: str
    category: COURSE_DOCUMENT_CATEGORIES
    sub_category: str | None
    created_at: datetime_utc
    updated_at: datetime_utc


class CourseDocumentCreate(BaseSchema):
    title: Annotated[str, StringConstraints(max_length=MAX_DOC_TITLE)]
    file_name: Annotated[str, StringConstraints(max_length=MAX_DOC_FILE_NAME)]
    course_id: int
    author: Annotated[str, StringConstraints(max_length=MAX_COURSE_DOC_AUTHOR)]
    category: COURSE_DOCUMENT_CATEGORIES = "Other"
    sub_category: Annotated[str, StringConstraints(max_length=MAX_COURSE_DOC_SUB_CATEGORY)] | None = None
    file: UploadFile


class CourseDocumentUpdate(BaseSchema):
    title: Annotated[str, StringConstraints(max_length=MAX_DOC_TITLE)]
    file_name: Annotated[str, StringConstraints(max_length=MAX_DOC_FILE_NAME)]
    author: Annotated[str, StringConstraints(max_length=MAX_COURSE_DOC_AUTHOR)]
    category: COURSE_DOCUMENT_CATEGORIES = "Other"
    sub_category: Annotated[str, StringConstraints(max_length=MAX_COURSE_DOC_SUB_CATEGORY)] | None = None
