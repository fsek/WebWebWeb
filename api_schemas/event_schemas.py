from typing import TYPE_CHECKING, Annotated
from api_schemas.base_schema import BaseSchema
from db_models.priority_model import Priority_DB
from helpers.constants import MAX_EVENT_DESC, MAX_EVENT_TITLE
from helpers.types import ALCOHOL_EVENT_TYPES, EVENT_DOT_TYPES, datetime_utc
from pydantic import StringConstraints

if TYPE_CHECKING:
    from api_schemas.council_schema import SimpleCouncilRead


class EventRead(BaseSchema):
    id: int
    council_id: int
    starts_at: datetime_utc
    ends_at: datetime_utc
    signup_start: datetime_utc
    signup_end: datetime_utc
    title_sv: str
    title_en: str
    description_sv: str
    description_en: str
    council: "SimpleCouncilRead"
    location: str
    max_event_users: int
    priorities: list[Priority_DB]
    all_day: bool
    recurring: bool
    food: bool
    closed: bool
    can_signup: bool
    drink_package: bool
    is_nollning_event: bool
    alcohol_event_type: str
    dress_code: str
    price: int
    signup_count: int
    dot: str
    lottery: bool


class EventPriorityRead(BaseSchema):
    priority: str


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
    location: str
    max_event_users: int
    priorities: list[str]
    all_day: bool
    recurring: bool
    food: bool
    closed: bool
    can_signup: bool
    drink_package: bool
    is_nollning_event: bool
    alcohol_event_type: ALCOHOL_EVENT_TYPES
    dress_code: str
    price: int
    dot: EVENT_DOT_TYPES
    lottery: bool


class EventUpdate(BaseSchema):
    council_id: int | None = None
    starts_at: datetime_utc | None = None
    ends_at: datetime_utc | None = None
    signup_start: datetime_utc | None = None
    signup_end: datetime_utc | None = None
    title_sv: Annotated[str, StringConstraints(max_length=MAX_EVENT_TITLE)] | None = None
    title_en: Annotated[str, StringConstraints(max_length=MAX_EVENT_TITLE)] | None = None
    description_sv: Annotated[str, StringConstraints(max_length=MAX_EVENT_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_EVENT_DESC)] | None = None
    location: str | None = None
    max_event_users: int | None = None
    all_day: bool | None = None
    recurring: bool | None = None
    food: bool | None = None
    closed: bool | None = None
    can_signup: bool | None = None
    drink_package: bool | None = None
    is_nollning_event: bool | None = None
    priorities: list[str] | None = None
    alcohol_event_type: ALCOHOL_EVENT_TYPES | None = None
    dress_code: str | None = None
    price: int | None = None
    dot: EVENT_DOT_TYPES | None = None


class AddEventTag(BaseSchema):
    event_id: int
    tag_id: int
