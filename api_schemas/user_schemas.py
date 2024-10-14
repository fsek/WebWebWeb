from typing import Annotated
from pydantic import StringConstraints
from fastapi_users_pelicanq import schemas as fastapi_users_schemas
from helpers.constants import MAX_FIRST_NAME_LEN, MAX_LAST_NAME_LEN
from api_schemas.base_schema import BaseSchema
from pydantic_extra_types.phone_numbers import PhoneNumber
from helpers.types import USER_FOOD_PREFERENCES, datetime_utc, USER_PROGRAMS
from typing import List 


class _UserEventRead(BaseSchema):
    id: int


class _UserPostRead(BaseSchema):
    id: int
    name: str
    council_id: int


class UserRead(fastapi_users_schemas.BaseUser[int], BaseSchema):
    first_name: str
    last_name: str
    email: str
    posts: list[_UserPostRead]
    events: list[_UserEventRead]
    telephone_number: PhoneNumber
    start_year: int
    account_created: datetime_utc
    food_preferences: List[USER_FOOD_PREFERENCES] 
    food_custom: str | None  
    program: USER_PROGRAMS | None


class UserSignupRead(fastapi_users_schemas.BaseUser[int], BaseSchema):
    first_name: str
    last_name: str
    email: str
    telephone_number: PhoneNumber
    start_year: int
    account_created: datetime_utc
    program: USER_PROGRAMS | None
    food_preferences: List[USER_FOOD_PREFERENCES] | None = None 
    food_custom: str | None = None
    want_notifications: bool


# fastapi-users will take all fields on this model and feed into the user constructor User_DB(...) when /auth/register route is called

class UserCreate(fastapi_users_schemas.BaseUserCreate, BaseSchema):
    first_name: Annotated[str, StringConstraints(max_length=MAX_FIRST_NAME_LEN)]
    last_name: Annotated[str, StringConstraints(max_length=MAX_LAST_NAME_LEN)]
    telephone_number: PhoneNumber | None = None
    start_year: int | None = None
    program: USER_PROGRAMS | None = None
    food_preferences: List[USER_FOOD_PREFERENCES] | None = None
    food_custom: str | None = None
    pass


class MeUpdate(BaseSchema):
    first_name: str | None = None
    last_name: str | None = None
    start_year: int | None = None
    program: USER_PROGRAMS | None = None
    food_preferences: List[USER_FOOD_PREFERENCES]| None = None
    food_custom: str | None = None
    notifications: bool | None = None


# class UserUpdate(fastapi_users_schemas.BaseUserUpdate, BaseSchema):
#     first_name: str
#     last_name: str
#     pass
