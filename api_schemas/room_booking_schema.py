from typing import Annotated
from helpers.types import datetime_utc
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_CAR_DESC


class RoomCreate(BaseSchema):
    description: Annotated[str, StringConstraints(max_length=MAX_CAR_DESC)] | None = None
    start_time: datetime_utc
    end_time: datetime_utc


class RoomRead(BaseSchema):
    booking_id: int
    user_id: int
    description: str
    start_time: datetime_utc
    end_time: datetime_utc


class RoomUpdate(BaseSchema):
    description: Annotated[str, StringConstraints(max_length=MAX_CAR_DESC)] | None = None
    start_time: datetime_utc | None = None
    end_time: datetime_utc | None = None
