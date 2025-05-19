from typing import Annotated
from helpers.types import datetime_utc
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_ROOM_DESC


class RoomCreate(BaseSchema):
    room_id: int
    start_time: datetime_utc
    end_time: datetime_utc
    description: Annotated[str, StringConstraints(max_length=MAX_ROOM_DESC)]
    council_id: int


class RoomRead(BaseSchema):
    booking_id: int
    room_id: int
    start_time: datetime_utc
    end_time: datetime_utc
    description: str
    user_id: int
    council_id: int


class RoomUpdate(BaseSchema):
    room_id: int | None = None
    start_time: datetime_utc | None = None
    end_time: datetime_utc | None = None
    description: Annotated[str, StringConstraints(max_length=MAX_ROOM_DESC)] | None = None
    council_id: int | None = None
