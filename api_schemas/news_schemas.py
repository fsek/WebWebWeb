from typing import Annotated
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from api_schemas.user_schemas import UserInNewsRead
from helpers.constants import MAX_NEWS_CONTENT, MAX_NEWS_TITLE
from helpers.types import datetime_utc


class NewsRead(BaseSchema):
    id: int
    title_sv: str
    title_en: str
    content_sv: str
    content_en: str
    author_id: int
    author: UserInNewsRead
    created_at: datetime_utc
    bumped_at: datetime_utc | None
    pinned_from: datetime_utc | None
    pinned_to: datetime_utc | None


class NewsCreate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_NEWS_TITLE)]
    title_en: Annotated[str, StringConstraints(max_length=MAX_NEWS_TITLE)]
    content_sv: Annotated[str, StringConstraints(max_length=MAX_NEWS_CONTENT)]
    content_en: Annotated[str, StringConstraints(max_length=MAX_NEWS_CONTENT)]
    pinned_from: datetime_utc | None = None
    pinned_to: datetime_utc | None = None


class NewsUpdate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_NEWS_TITLE)] | None = None
    title_en: Annotated[str, StringConstraints(max_length=MAX_NEWS_TITLE)] | None = None
    content_sv: Annotated[str, StringConstraints(max_length=MAX_NEWS_CONTENT)] | None = None
    content_en: Annotated[str, StringConstraints(max_length=MAX_NEWS_CONTENT)] | None = None
    pinned_from: datetime_utc | None = None
    pinned_to: datetime_utc | None = None
