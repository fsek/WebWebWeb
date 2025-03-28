from api_schemas.user_schemas import SimpleUserRead
from helpers.types import datetime_utc
from api_schemas.base_schema import BaseSchema


class DocumentUpload(BaseSchema):
    name: str
    uploader_id: int
    document: None


class DocumentLoad(BaseSchema):
    id: int


class DocumentOverview(BaseSchema):
    name: str
    upload_date: datetime_utc
    upload_user: SimpleUserRead
