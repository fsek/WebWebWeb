from typing import TYPE_CHECKING, Annotated
from api_schemas.base_schema import BaseSchema
from api_schemas.event_signup_schemas import EventSignupRead
from db_models.priority_model import Priority_DB
from helpers.constants import MAX_EVENT_DESC, MAX_EVENT_TITLE
from helpers.types import MEMBER_ROLES, datetime_utc
from pydantic import StringConstraints

if TYPE_CHECKING:
    from api_schemas.council_schema import CouncilInEventRead


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
    council: "CouncilInEventRead"
    location: str
    max_event_users: int
    priorities: list[Priority_DB]
    all_day: bool
    signup_not_opened_yet: bool
    recurring: bool
    drink: bool
    food: bool
    cash: bool
    closed: bool
    can_signup: bool
    drink_package: bool
    is_nollning_event: bool


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
    priorities: list[MEMBER_ROLES]
    all_day: bool
    signup_not_opened_yet: bool
    recurring: bool
    drink: bool
    food: bool
    cash: bool
    closed: bool
    can_signup: bool
    drink_package: bool
    is_nollning_event: bool


class EventUpdate(BaseSchema):
    starts_at: datetime_utc | None = None
    ends_at: datetime_utc | None = None
    signup_start: datetime_utc | None = None
    signup_end: datetime_utc | None = None
    title_sv: Annotated[str, StringConstraints(max_length=MAX_EVENT_TITLE)] | None = None
    title_en: Annotated[str, StringConstraints(max_length=MAX_EVENT_TITLE)] | None = None
    description_sv: Annotated[str, StringConstraints(max_length=MAX_EVENT_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_EVENT_DESC)] | None = None
    location: str
    max_event_users: int | None = None
    all_day: bool | None = None
    signup_not_opened_yet: bool | None = None
    recurring: bool | None = None
    drink: bool | None = None
    food: bool | None = None
    cash: bool | None = None
    closed: bool | None = None
    can_signup: bool | None = None
    drink_package: bool | None = None
    is_nollning_event: bool | None = None


class AddEventTag(BaseSchema):
    event_id: int
    tag_id: int
