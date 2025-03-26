from api_schemas.base_schema import BaseSchema
from api_schemas.event_schemas import EventRead
from api_schemas.post_schemas import PostRead


class CouncilCreate(BaseSchema):
    name: str


class CouncilRead(BaseSchema):
    id: int
    name: str
    posts: list[PostRead]
    events: list[EventRead]


class CouncilUpdate(BaseSchema):
    name: str | None = None
