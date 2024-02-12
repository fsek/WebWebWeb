import datetime
from typing import Annotated
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_EVENT_DESC, MAX_EVENT_TITLE
from pydantic import StringConstraints


class EventRead(BaseSchema):
    id: int
    starts_at: datetime.datetime
    ends_at: datetime.datetime
    title_sv: str
    title_en: str
    description_sv: str
    description_en: str
    max_event_users: int


# we dont need to be as strict about out data as in data.
# str is fine for Read but Create needs max_length, good validation


class EventCreate(BaseSchema):
    council_id: int
    starts_at: datetime.datetime
    ends_at: datetime.datetime
    signup_start: datetime.datetime
    signup_end: datetime.datetime
    title_sv: Annotated[str, StringConstraints(max_length=MAX_EVENT_TITLE)]
    title_en: Annotated[str, StringConstraints(max_length=MAX_EVENT_TITLE)]
    description_sv: Annotated[str, StringConstraints(max_length=MAX_EVENT_DESC)]
    description_en: Annotated[str, StringConstraints(max_length=MAX_EVENT_DESC)]
    max_event_users: int


class EventUpdate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_EVENT_TITLE)] | None = None
    title_en: Annotated[str, StringConstraints(max_length=MAX_EVENT_TITLE)] | None = None
    description_sv: Annotated[str, StringConstraints(max_length=MAX_EVENT_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_EVENT_DESC)] | None = None
    max_event_users: int | None = None
