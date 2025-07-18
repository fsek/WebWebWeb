from typing import Annotated
from helpers.types import datetime_utc
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_CAR_DESC
from api_schemas.council_schema import CouncilInCarBookingRead


class CarBookingRead(BaseSchema):
    booking_id: int
    user_id: int
    user_first_name: str
    user_last_name: str
    description: str
    start_time: datetime_utc
    end_time: datetime_utc
    confirmed: bool
    personal: bool
    council_id: int | None = None
    council: CouncilInCarBookingRead | None = None


class CarBookingCreate(BaseSchema):
    description: Annotated[str, StringConstraints(max_length=MAX_CAR_DESC)]
    start_time: datetime_utc
    end_time: datetime_utc
    personal: bool
    council_id: int | None = None


class CarBookingUpdate(BaseSchema):
    description: Annotated[str, StringConstraints(max_length=MAX_CAR_DESC)] | None = None
    start_time: datetime_utc | None = None
    end_time: datetime_utc | None = None
    confirmed: bool | None = None
    personal: bool | None = None
    council_id: int | None = None
