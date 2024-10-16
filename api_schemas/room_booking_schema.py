from helpers.types import datetime_utc
from api_schemas.base_schema import BaseSchema
from helpers.types import COMMITIEES

# from typing import Annotated
# from pydantic import StringConstraints


class RoomRead(BaseSchema):
    booking_id: int
    user_id: int
    description: str
    start_time: datetime_utc
    end_time: datetime_utc
    council_id: int


class RoomCreate(BaseSchema):
    description: str | None = None
    start_time: datetime_utc
    end_time: datetime_utc
    council_id: int


class RoomUpdate(BaseSchema):
    description: str | None = None
    start_time: datetime_utc | None = None
    end_time: datetime_utc | None = None
    council_id: int | None = None
