from api_schemas.base_schema import BaseSchema
from helpers.types import datetime_utc


class NominationRead(BaseSchema):
    nomination_id: int
    sub_election_id: int
    nominee_name: str
    nominee_email: str
    motivation: str
    created_at: datetime_utc
    post_id: int
    election_post_id: int


class NominationCreate(BaseSchema):
    sub_election_id: int
    nominee_name: str
    nominee_email: str
    motivation: str
    election_post_id: int
