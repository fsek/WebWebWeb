from typing import Annotated
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_EVENT_DESC, MAX_EVENT_TITLE
from helpers.types import datetime_utc
from pydantic import StringConstraints


class CafeShiftRead(BaseSchema):
    worker_id: int
    is_me: bool
    starts_at: datetime_utc
    ends_at: datetime_utc


class CafeShiftCreate(BaseSchema):
    starts_at: datetime_utc
    ends_at: datetime_utc


class CafeShiftUpdate(BaseSchema):
    starts_at: datetime_utc | None = None
    ends_at: datetime_utc | None = None
    cafe_worker_id: int | None = None
