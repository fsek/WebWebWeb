from api_schemas.adventure_mission_schema import AdventureMissionRead
from api_schemas.base_schema import BaseSchema
from api_schemas.group_schema import GroupRead


class NollningCreate(BaseSchema):
    name: str
    year: int
    description: str


class NollningGroupRead(BaseSchema):
    id: int
    group: GroupRead
    nollning_id: int
    mentor_group_number: int | None = None


class NollningRead(NollningCreate):
    id: int
    year: int
    missions: list[AdventureMissionRead]
    nollning_groups: list[NollningGroupRead]


class NollningAddGroup(BaseSchema):
    group_id: int
    mentor_group_number: int | None = None
