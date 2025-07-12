from api_schemas.base_schema import BaseSchema
from api_schemas.post_schemas import PostRead
from api_schemas.event_schemas import EventRead


class CouncilCreate(BaseSchema):
    name: str
    description: str | None = None


class CouncilRead(BaseSchema):
    id: int
    name: str
    posts: list[PostRead]
    events: list[EventRead]
    description: str | None


class CouncilUpdate(BaseSchema):
    name: str | None = None
    description: str | None = None


class CouncilInEventRead(BaseSchema):
    id: int
    name: str


class CouncilInCarRead(BaseSchema):
    id: int
    name: str
