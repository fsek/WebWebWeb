from helpers.types import datetime_utc
from api_schemas.base_schema import BaseSchema
from helpers.types import COMMITIEES


class RoomRead(BaseSchema):
    booking_id: int
    user_id: int
    description: str
    start_time: datetime_utc
    end_time: datetime_utc
    commitiees: COMMITIEES


class RoomCreate(BaseSchema):
    description: str | None = None
    start_time: datetime_utc
    end_time: datetime_utc
    commitiees: list[COMMITIEES]


class RoomUpdate(BaseSchema):
    description: str | None = None
    start_time: datetime_utc | None = None
    end_time: datetime_utc | None = None
    # Change?
    commitiees: COMMITIEES | None = None
