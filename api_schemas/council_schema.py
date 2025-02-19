from api_schemas.base_schema import BaseSchema
from api_schemas.event_schemas import EventRead
from api_schemas.post_schemas import PostRead


class CouncilExempel(BaseSchema):
    exemple_value: int


class CouncilRead(BaseSchema):
    id: int
    name: str
    posts: list[PostRead]
    events: list[EventRead]
