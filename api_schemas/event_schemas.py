from typing import Annotated
from api_schemas.base_schema import BaseSchema
from db_models.priority_model import Priority_DB
from helpers.constants import MAX_EVENT_DESC, MAX_EVENT_TITLE
from helpers.types import MEMBER_ROLES, datetime_utc
from pydantic import StringConstraints


class EventRead(BaseSchema):
    id: int
    starts_at: datetime_utc
    ends_at: datetime_utc
    signup_start: datetime_utc
    signup_end: datetime_utc
    title_sv: str
    title_en: str
    description_sv: str
    description_en: str
    max_event_users: int
    priorities: list[Priority_DB]


# we dont need to be as strict about out data as in data.
# str is fine for Read but Create needs max_length, good validation


class EventCreate(BaseSchema):
    council_id: int
    starts_at: datetime_utc
    ends_at: datetime_utc
    signup_start: datetime_utc
    signup_end: datetime_utc
    title_sv: Annotated[str, StringConstraints(max_length=MAX_EVENT_TITLE)]
    title_en: Annotated[str, StringConstraints(max_length=MAX_EVENT_TITLE)]
    description_sv: Annotated[str, StringConstraints(max_length=MAX_EVENT_DESC)]
    description_en: Annotated[str, StringConstraints(max_length=MAX_EVENT_DESC)]
    max_event_users: int
    priorities: list[MEMBER_ROLES]
    all_day: bool | None = False
    signup_not_opened_yet: bool
    recurring: bool | None = False
    drink: bool | None = False
    food: bool | None = False
    cash: bool | None = False
    closed: bool | None = False
    can_signup: bool | None = False
    drink_package: bool | None = False


class EventUpdate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_EVENT_TITLE)] | None = None
    title_en: Annotated[str, StringConstraints(max_length=MAX_EVENT_TITLE)] | None = None
    description_sv: Annotated[str, StringConstraints(max_length=MAX_EVENT_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_EVENT_DESC)] | None = None
    max_event_users: int | None = None
    signup_not_opened_yet: bool | None = None
    closed: bool | None = None
    can_signup: bool | None = None
