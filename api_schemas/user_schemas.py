from typing import Annotated
from pydantic import StringConstraints
from fastapi_users import schemas as fastapi_users_schemas
from helpers.constants import MAX_FIRSTNAME_LEN, MAX_LASTNAME_LEN
from api_schemas.base_schema import BaseSchema


class _UserEventRead(BaseSchema):
    id: int


class _UserPostRead(BaseSchema):
    id: int
    name: str
    council_id: int


class UserRead(fastapi_users_schemas.BaseUser[int], BaseSchema):
    firstname: str
    lastname: str
    email: str
    posts: list[_UserPostRead]
    events: list[_UserEventRead]


# fastapi-users will take all fields on this model and feed into the user constructor User_DB(...) when /auth/register route is called
class UserCreate(fastapi_users_schemas.BaseUserCreate, BaseSchema):
    firstname: Annotated[str, StringConstraints(max_length=MAX_FIRSTNAME_LEN)]
    lastname: Annotated[str, StringConstraints(max_length=MAX_LASTNAME_LEN)]
    pass


class MeUpdate(BaseSchema):
    firstname: str | None = None
    lastname: str | None = None


# class UserUpdate(fastapi_users_schemas.BaseUserUpdate, BaseSchema):
#     firstname: str
#     lastname: str
#     pass
