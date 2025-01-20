from api_schemas.base_schema import BaseSchema
from api_schemas.event_schemas import EventRead
from api_schemas.news_schemas import NewsRead
from api_schemas.nollning_schema import NollningRead
from helpers.types import TAG_TYPE


class TagCreate(BaseSchema):
    name: str
    tag_type: TAG_TYPE
    target_id: int


class TagRead(BaseSchema):
    id: int
    tag_type: TAG_TYPE


class NollningTagRead(BaseSchema):
    name: str
    tag: TagRead
    nollning: NollningRead


class EventTagRead(BaseSchema):
    name: str
    tag: TagRead
    event: EventRead


class CafeTagRead(BaseSchema):
    name: str
    tag: TagRead


class NewsTagRead(BaseSchema):
    name: str
    tag: TagRead
    news: NewsRead


class AlbumTagRead(BaseSchema):
    name: str
    tag: TagRead
