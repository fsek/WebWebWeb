from api_schemas.adventure_mission_schema import AdventureMissionRead
from api_schemas.base_schema import BaseSchema
from api_schemas.group_schema import GroupRead


class NollningCreate(BaseSchema):
    name: str
    description: str


class NollningGroupRead(BaseSchema):
    id: int
    group: GroupRead
    nollning_id: int


class NollningRead(NollningCreate):
    id: int
    missions: list[AdventureMissionRead]
    nollning_groups: list[NollningGroupRead]


class NollningAddGroup(BaseSchema):
    group_id: int


class NollningDeleteMission(BaseSchema):
    group_id: int
    mission_id: int
