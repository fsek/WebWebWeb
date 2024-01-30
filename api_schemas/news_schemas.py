from datetime import datetime
from typing import Annotated

from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_NEWS_CONTENT, MAX_NEWS_TITLE


class NewsRead(BaseSchema):
    id: int
    title_sv: str
    title_en: str
    content_sv: str
    content_en: str
    author_id: int
    pinned_from: datetime
    pinned_to: datetime


class NewsCreate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_NEWS_TITLE)]
    title_en: Annotated[str, StringConstraints(max_length=MAX_NEWS_TITLE)]
    content_sv: Annotated[str, StringConstraints(max_length=MAX_NEWS_CONTENT)]
    content_en: Annotated[str, StringConstraints(max_length=MAX_NEWS_CONTENT)]
    pinned_from: datetime | None
    pinned_to: datetime | None


class NewsUpdate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_NEWS_TITLE)] | None
    title_en: Annotated[str, StringConstraints(max_length=MAX_NEWS_TITLE)] | None
    content_sv: Annotated[str, StringConstraints(max_length=MAX_NEWS_CONTENT)] | None
    content_en: Annotated[str, StringConstraints(max_length=MAX_NEWS_CONTENT)] | None
    pinned_from: datetime | None
    pinned_to: datetime | None
