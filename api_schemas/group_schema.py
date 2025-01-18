from typing import Annotated
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from api_schemas.user_schemas import UserInGroupRead
from helpers.constants import MAX_GROUP_NAME
from helpers.types import GROUP_TYPE, GROUP_USER_TYPE


class GroupCreate(BaseSchema):
    name: Annotated[str, StringConstraints(max_length=MAX_GROUP_NAME)]
    group_type: GROUP_TYPE


class GroupUserRead(BaseSchema):
    user: UserInGroupRead
    group_user_type: GROUP_USER_TYPE


class GroupRead(BaseSchema):
    id: int
    name: str
    group_type: GROUP_TYPE
    group_users: list[GroupUserRead]


class GroupAddUser(BaseSchema):
    user_id: int
    group_user_type: GROUP_USER_TYPE


class GroupRemoveUser(BaseSchema):
    user_id: int
