from typing import Annotated
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from api_schemas.user_schemas import UserInGroupRead


class GroupMissionCreate(BaseSchema):
    points: int
    nollning_group_id: int
    adventure_mission_id: int


class GroupMissionRead(BaseSchema):
    pass
