from datetime import datetime
from api_schemas.base_schema import BaseSchema
from db_models.adventure_mission_model import AdventureMission_DB


class AdventureMissionCreate(BaseSchema):
    title: str
    description: str
    points: str
    nollning_id: int
    nollning_week: int


class AdventureMissionRead(BaseSchema):
    id: int
    title: str
    description: str
    points: str
    nollning_id: int
    nollning_week: int
    created_at: datetime
