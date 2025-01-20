from api_schemas.base_schema import BaseSchema
from api_schemas.event_schemas import EventRead
from api_schemas.news_schemas import NewsRead


class TagCreate(BaseSchema):
    name: str


class NewsTagRead(BaseSchema):
    news: NewsRead


class EventTagRead(BaseSchema):
    event: EventRead


class TagRead(BaseSchema):
    id: int
    name: str
    news_tags: list[NewsTagRead]
    event_tags: list[EventTagRead]
