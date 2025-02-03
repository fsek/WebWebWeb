from api_schemas.adventure_mission_schema import AdventureMissionRead
from api_schemas.nollning_schema import NollningGroupRead
from builtins import int
from typing import Annotated
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from api_schemas.user_schemas import UserInGroupRead


class GroupMissionCreate(BaseSchema):
    points: int
    adventure_mission_id: int


class GroupMissionRead(BaseSchema):
    points: int
    adventure_mission: AdventureMissionRead
    nollning_group: NollningGroupRead
