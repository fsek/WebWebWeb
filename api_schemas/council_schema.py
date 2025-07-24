from api_schemas.base_schema import BaseSchema
from api_schemas.post_schemas import PostRead
from api_schemas.event_schemas import EventRead


class CouncilCreate(BaseSchema):
    name_sv: str
    name_en: str
    description_sv: str | None = None
    description_en: str | None = None


class CouncilRead(BaseSchema):
    id: int
    name_sv: str
    name_en: str
    posts: list[PostRead]
    events: list[EventRead]
    description_sv: str | None
    description_en: str | None


class CouncilUpdate(BaseSchema):
    name_sv: str | None = None
    name_en: str | None = None
    description_sv: str | None = None
    description_en: str | None = None


class SimpleCouncilRead(BaseSchema):
    id: int
    name_sv: str
    name_en: str
