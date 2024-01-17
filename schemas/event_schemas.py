import datetime
from schemas.user_schemas import BaseSchema


class EventRead(BaseSchema):
    id: int
    starts_at: datetime.datetime
    ends_at: datetime.datetime


class EventCreate(BaseSchema):
    council_id: int
    starts_at: datetime.datetime
    ends_at: datetime.datetime
    description_sv: str
    description_en: str
