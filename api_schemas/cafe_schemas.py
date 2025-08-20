from api_schemas.base_schema import BaseSchema
from api_schemas.user_schemas import SimpleUserRead, AdminUserReadForCafeShifts
from helpers.types import datetime_utc


class BaseCafeShiftRead(BaseSchema):
    id: int
    user_id: int | None
    starts_at: datetime_utc
    ends_at: datetime_utc


class CafeShiftRead(BaseCafeShiftRead):
    user: SimpleUserRead | None


class AdminCafeShiftRead(BaseCafeShiftRead):
    user: AdminUserReadForCafeShifts | None


class CafeShiftCreate(BaseSchema):
    starts_at: datetime_utc
    ends_at: datetime_utc


class CafeShiftCreateMulti(BaseSchema):
    startWeekStart: datetime_utc
    endWeekStart: datetime_utc


class CafeShiftUpdate(BaseSchema):
    starts_at: datetime_utc | None = None
    ends_at: datetime_utc | None = None
    user_id: int | None = None


class CafeViewBetweenDates(BaseSchema):
    start_date: datetime_utc
    end_date: datetime_utc
