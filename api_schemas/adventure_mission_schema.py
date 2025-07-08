from datetime import datetime
from api_schemas.base_schema import BaseSchema


class AdventureMissionCreate(BaseSchema):
    title: str
    description: str
    max_points: int
    min_points: int
    nollning_id: int
    nollning_week: int


class AdventureMissionRead(BaseSchema):
    id: int
    title: str
    description: str
    max_points: int
    min_points: int
    nollning_id: int
    nollning_week: int
    created_at: datetime
