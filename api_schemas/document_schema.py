from types import NoneType
from api_schemas.user_schemas import SimpleUserRead
from helpers.types import datetime_utc
from api_schemas.base_schema import BaseSchema
from typing import Annotated
from fastapi import FastAPI, File, UploadFile


class DocCreate(BaseSchema):
    File: UploadFile


class DocInAlbum(BaseSchema):
    id: int


class DocumentUpload(BaseSchema):
    name: str
    uploader_id: int


class DocumentLoad(BaseSchema):
    id: int


class DocumentOverview(BaseSchema):
    name: str
    date_uploaded: datetime_utc
    upload_user: SimpleUserRead


class DocumentView(BaseSchema):
    name: str
    upload_date: datetime_utc
    upload_user: SimpleUserRead
    document: None


class DocumentUpdate(BaseSchema):
    id: int
    name: str | None
    document: str | None
