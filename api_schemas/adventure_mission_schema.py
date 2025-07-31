from datetime import datetime
from api_schemas.base_schema import BaseSchema


class AdventureMissionCreate(BaseSchema):
    title_sv: str
    title_en: str
    description_sv: str
    description_en: str
    max_points: int
    min_points: int
    nollning_week: int


class AdventureMissionRead(BaseSchema):
    id: int
    title_sv: str
    title_en: str
    description_sv: str
    description_en: str
    max_points: int
    min_points: int
    nollning_id: int
    nollning_week: int
    created_at: datetime
