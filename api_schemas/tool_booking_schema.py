from typing import Annotated
from api_schemas.tool_schema import SimpleToolRead
from api_schemas.user_schemas import SimpleUserRead
from helpers.types import datetime_utc
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_TOOL_BOOKING_DESC


class ToolBookingCreate(BaseSchema):
    tool_id: int
    amount: int
    start_time: datetime_utc
    end_time: datetime_utc
    description: Annotated[str, StringConstraints(max_length=MAX_TOOL_BOOKING_DESC)]


class ToolBookingRead(BaseSchema):
    id: int
    tool: SimpleToolRead
    amount: int
    user: SimpleUserRead
    start_time: datetime_utc
    end_time: datetime_utc
    description: str


class ToolBookingUpdate(BaseSchema):
    amount: int | None = None
    start_time: datetime_utc | None = None
    end_time: datetime_utc | None = None
    description: Annotated[str, StringConstraints(max_length=MAX_TOOL_BOOKING_DESC)] | None = None
