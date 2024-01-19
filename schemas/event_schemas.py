import datetime
from typing import Annotated
from schemas.user_schemas import BaseSchema
from pydantic import StringConstraints


class EventRead(BaseSchema):
    id: int
    starts_at: datetime.datetime
    ends_at: datetime.datetime
    title_sv: str
    title_en: str
    description_sv: str
    description_en: str


# we dont need to be as strict about out data as in data.
# str is fine for Read but Create needs max_length


class EventCreate(BaseSchema):
    council_id: int
    starts_at: datetime.datetime
    ends_at: datetime.datetime
    title_sv: Annotated[str, StringConstraints(max_length=100)]
    title_en: Annotated[str, StringConstraints(max_length=100)]
    description_sv: Annotated[str, StringConstraints(max_length=1000)]
    description_en: Annotated[str, StringConstraints(max_length=1000)]
