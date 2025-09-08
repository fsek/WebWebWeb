from pydantic_extra_types.phone_numbers import PhoneNumber
from api_schemas.base_schema import BaseSchema
from helpers.types import PROGRAM_TYPE, datetime_utc


# Only admins should have access to any of these three schemas
class CandidateUserRead(BaseSchema):
    first_name: str
    last_name: str
    email: str
    telephone_number: PhoneNumber
    stil_id: str | None
    start_year: int
    program: PROGRAM_TYPE


class CandidatePostRead(BaseSchema):
    candidate_id: int
    post_id: int
    election_post_id: int
    sub_election_id: int
    created_at: datetime_utc


class CandidateRead(BaseSchema):
    candidate_id: int
    sub_election_id: int
    user_id: int
    user: CandidateUserRead
    candidations: list[CandidatePostRead]
