from api_schemas.user_schemas import SimpleUserRead
from helpers.types import datetime_utc
from api_schemas.base_schema import BaseSchema


class DocumentCreate(BaseSchema):
    name: str
    uploader_user_id: int
    document: None


class DocumentGet(BaseSchema):
    id: int


class DocumentRead(BaseSchema):
    name: str
    upload_date: datetime_utc
    upload_user: SimpleUserRead
