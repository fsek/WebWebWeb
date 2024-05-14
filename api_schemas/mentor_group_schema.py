from typing import Annotated
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from api_schemas.user_schemas import GroupUserRead
from helpers.constants import MAX_GROUP_NAME


class MentorGroupCreate(BaseSchema):
    name: Annotated[str, StringConstraints(max_length=MAX_GROUP_NAME)]
    group_type: str


class MentorGroupRead(BaseSchema):
    id: int
    name: str
    group_type: str
    group_users: list[GroupUserRead]
