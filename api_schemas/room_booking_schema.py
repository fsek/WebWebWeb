from helpers.types import datetime_utc
from api_schemas.base_schema import BaseSchema


class RoomRead(BaseSchema):
    booking_id: int
    user_id: int
    council_id: int
    description: str | None = None
    start_time: datetime_utc
    end_time: datetime_utc



class RoomCreate(BaseSchema):
    booking_id: int
    user_id: int
    council_id: int
    description: str | None = None
    start_time: datetime_utc
    end_time: datetime_utc

    


class RoomUpdate(BaseSchema):
    description: str | None = None
    start_time: datetime_utc | None = None
    end_time: datetime_utc | None = None
