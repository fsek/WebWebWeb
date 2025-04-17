from typing import TYPE_CHECKING, Annotated, Literal
from pydantic import StringConstraints
from fastapi_users_pelicanq import schemas as fastapi_users_schemas
from helpers.constants import MAX_FIRST_NAME_LEN, MAX_LAST_NAME_LEN
from api_schemas.base_schema import BaseSchema
from pydantic_extra_types.phone_numbers import PhoneNumber
from helpers.types import DOOR_ACCESSES, datetime_utc


class _UserEventRead(BaseSchema):
    id: int


class _UserPostRead(BaseSchema):
    id: int
    name: str
    council_id: int


class SimpleUserRead(BaseSchema):
    id: int
    first_name: str
    last_name: str


####   USER ACCESS   ####


class UserAccessCreate(BaseSchema):
    user_id: int
    door: Literal[DOOR_ACCESSES]
    starttime: datetime_utc
    stoptime: datetime_utc


class UserAccessRead(BaseSchema):
    user_access_id: int
    user: SimpleUserRead
    door: str
    starttime: datetime_utc
    stoptime: datetime_utc


class SimpleUserAccessRead(BaseSchema):
    door: str
    starttime: datetime_utc
    stoptime: datetime_utc


class UserAccessUpdate(BaseSchema):
    access_id: int
    door: Literal[DOOR_ACCESSES] | None = None
    starttime: datetime_utc | None = None
    stoptime: datetime_utc | None = None


#################################


class UserRead(fastapi_users_schemas.BaseUser[int], BaseSchema):
    first_name: str
    last_name: str
    email: str
    posts: list[_UserPostRead]
    events: list[_UserEventRead]
    telephone_number: PhoneNumber
    start_year: int
    account_created: datetime_utc
    want_notifications: bool
    stil_id: str | None = None
    accesses: list[SimpleUserAccessRead]


class UserInGroupRead(fastapi_users_schemas.BaseUser[int], BaseSchema):
    first_name: str
    last_name: str
    program: str | None


# fastapi-users will take all fields on this model and feed into the user constructor User_DB(...) when /auth/register route is called
class UserCreate(fastapi_users_schemas.BaseUserCreate, BaseSchema):
    first_name: Annotated[str, StringConstraints(max_length=MAX_FIRST_NAME_LEN)]
    last_name: Annotated[str, StringConstraints(max_length=MAX_LAST_NAME_LEN)]
    telephone_number: PhoneNumber | None = None
    start_year: int | None = None
    program: str | None = None
    pass


class UserUpdate(BaseSchema):
    first_name: str | None = None
    last_name: str | None = None
    start_year: int | None = None
    program: str | None = None
    notifications: bool | None = None
    stil_id: str | None = None


class UpdateUserMember(BaseSchema):
    is_member: bool
