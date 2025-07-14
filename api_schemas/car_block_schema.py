from api_schemas.base_schema import BaseSchema
from helpers.types import datetime_utc


class CarBlockRead(BaseSchema):
    id: int
    user_id: int
    reason: str
    blocked_by: int
    created_at: datetime_utc | None = None


class CarBlockCreate(BaseSchema):
    user_id: int
    reason: str
