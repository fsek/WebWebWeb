from typing import Annotated
from api_schemas.council_schema import SimpleCouncilRead
from api_schemas.user_schemas import SimpleUserRead
from helpers.types import ROOMS, datetime_utc
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_ROOM_DESC


class RoomBookingCreate(BaseSchema):
    room: ROOMS
    start_time: datetime_utc
    end_time: datetime_utc
    description: Annotated[str, StringConstraints(max_length=MAX_ROOM_DESC)]
    council_id: int
    recur_interval_days: int | None = None  # Set this to None if you don't want a recurring event
    recur_until: datetime_utc | None = None


class RoomBookingRead(BaseSchema):
    id: int
    room: str
    start_time: datetime_utc
    end_time: datetime_utc
    description: str
    user: SimpleUserRead
    council: SimpleCouncilRead


class RoomBookingUpdate(BaseSchema):
    start_time: datetime_utc | None = None
    end_time: datetime_utc | None = None
    description: Annotated[str, StringConstraints(max_length=MAX_ROOM_DESC)] | None = None


class RoomBookingsBetweenDates(BaseSchema):
    start_time: datetime_utc
    end_time: datetime_utc
