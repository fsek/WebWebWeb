from api_schemas.adventure_mission_schema import AdventureMissionRead
from api_schemas.nollning_schema import NollningGroupRead
from builtins import int
from api_schemas.base_schema import BaseSchema
from helpers.types import MISSION_CONFIRMED_TYPES


class GroupMissionCreate(BaseSchema):
    points: int
    adventure_mission_id: int


class GroupMissionEdit(BaseSchema):
    points: int | None = None
    adventure_mission_id: int | None = None
    is_accepted: MISSION_CONFIRMED_TYPES | None = None


class GroupMissionRead(BaseSchema):
    points: int
    adventure_mission: AdventureMissionRead
    nollning_group: NollningGroupRead
    is_accepted: str
