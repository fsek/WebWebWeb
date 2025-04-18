from api_schemas.base_schema import BaseSchema
from fastapi_users_pelicanq import schemas as fastapi_users_schemas
from pydantic_extra_types.phone_numbers import PhoneNumber
from api_schemas.user_schemas import UserInEventRead, UserRead
from helpers.types import datetime_utc


class EventSignupCreate(BaseSchema):
    user_id: int | None = None
    priority: str | None = None
    group_name: str | None = None


class EventSignupRead(BaseSchema):
    user: UserInEventRead
    event_id: int
    priority: str
    group_name: str


class EventSignupUpdate(BaseSchema):
    user_id: int | None = None
    priority: str | None = None
    group_name: str | None = None


class EventSignupDelete(BaseSchema):
    user_id: int | None = None
