from typing import Annotated
from fastapi import Form, UploadFile
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from api_schemas.user_schemas import SimpleUserRead
from helpers.constants import MAX_DOC_TITLE
from helpers.types import datetime_utc


class DocumentRead(BaseSchema):
    id: int
    title: str
    file_name: str
    category: str
    author_id: int
    author: SimpleUserRead
    created_at: datetime_utc
    updated_at: datetime_utc
    is_private: bool


class DocumentCreate(BaseSchema):
    title: Annotated[str, StringConstraints(max_length=MAX_DOC_TITLE)]
    category: str
    is_private: bool


# Apparently I have to do this to be able to send JSON forms at the same time as files in the POST document router
def document_create_form(
    title: str = Form(...),
    category: str = Form(...),
    is_private: bool = Form(...),
) -> DocumentCreate:
    return DocumentCreate(title=title, category=category, is_private=is_private)


class DocumentUpdate(BaseSchema):
    title: Annotated[str, StringConstraints(max_length=MAX_DOC_TITLE)] | None = None
    category: str | None = None
    is_private: bool | None = None
