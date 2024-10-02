from api_schemas.base_schema import BaseSchema
from fastapi_users_pelicanq import schemas as fastapi_users_schemas
from pydantic_extra_types.phone_numbers import PhoneNumber
from helpers.types import datetime_utc


class EventSignupCreate(BaseSchema):
    user_id: int | None = None
    priority: str | None = None
    group_name: str | None = None


class EventSignupRead(fastapi_users_schemas.BaseUser[int], BaseSchema):
    first_name: str
    last_name: str
    email: str
    telephone_number: PhoneNumber
    start_year: int
    account_created: datetime_utc
    program: str | None
    priority: str | None
    group_name: str | None


class EventSignupUpdate(BaseSchema):
    user_id: int | None = None
    priority: str | None = None
    group_name: str | None = None


class EventSignupDelete(BaseSchema):
    user_id: int | None = None
