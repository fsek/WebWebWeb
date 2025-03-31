from api_schemas.base_schema import BaseSchema
from api_schemas.event_schemas import EventRead
from api_schemas.post_schemas import PostRead


class CouncilCreate(BaseSchema):
    name: str
    description: str | None = None


class CouncilRead(BaseSchema):
    id: int
    name: str
    posts: list[PostRead]
    events: list[EventRead]
    description: str | None
