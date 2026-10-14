from typing import Annotated
from api_schemas.equipment_schema import SimpleEquipmentRead
from api_schemas.user_schemas import SimpleUserRead
from helpers.types import datetime_utc
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_EQUIPMENT_BOOKING_DESC


class EquipmentBookingCreate(BaseSchema):
    equipment_id: int
    amount: int
    start_time: datetime_utc
    end_time: datetime_utc
    description: Annotated[str, StringConstraints(max_length=MAX_EQUIPMENT_BOOKING_DESC)]


class EquipmentBookingRead(BaseSchema):
    id: int
    equipment: SimpleEquipmentRead
    amount: int
    user: SimpleUserRead
    start_time: datetime_utc
    end_time: datetime_utc
    description: str | None


class SimpleEquipmentBookingRead(BaseSchema):
    id: int
    equipment: SimpleEquipmentRead
    amount: int
    start_time: datetime_utc
    end_time: datetime_utc
    description: str | None


class EquipmentBookingUpdate(BaseSchema):
    amount: int | None = None
    start_time: datetime_utc | None = None
    end_time: datetime_utc | None = None
    description: Annotated[str, StringConstraints(max_length=MAX_EQUIPMENT_BOOKING_DESC)] | None = None
