from typing import Annotated
from api_schemas.base_schema import BaseSchema
from api_schemas.user_schemas import SimpleUserRead
from helpers.constants import MAX_EVENT_DESC, MAX_EVENT_TITLE
from helpers.types import datetime_utc
from pydantic import StringConstraints


class CafeShiftRead(BaseSchema):
    id: int
    user_id: int | None
    user: SimpleUserRead | None
    starts_at: datetime_utc
    ends_at: datetime_utc


class CafeShiftCreate(BaseSchema):
    starts_at: datetime_utc
    ends_at: datetime_utc


class CafeShiftUpdate(BaseSchema):
    starts_at: datetime_utc | None = None
    ends_at: datetime_utc | None = None
    user_id: int | None = None


class CafeViewBetweenDates(BaseSchema):
    start_date: datetime_utc
    end_date: datetime_utc
