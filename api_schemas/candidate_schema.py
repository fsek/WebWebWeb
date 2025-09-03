from pydantic_extra_types.phone_numbers import PhoneNumber
from api_schemas.base_schema import BaseSchema
from helpers.types import datetime_utc, PROGRAM_TYPE


class CandidateUserRead(BaseSchema):
    first_name: str
    last_name: str
    email: str
    telephone_number: PhoneNumber
    start_year: int
    program: PROGRAM_TYPE


class CandidatePostRead(BaseSchema):
    post_id: int
    election_post_id: int


class CandidateRead(BaseSchema):
    candidate_id: int
    election_id: int
    user_id: int
    user: CandidateUserRead
    election_posts: list[CandidatePostRead]


class CandidateElectionRead(BaseSchema):
    candidate_id: int
    user_id: int
    user: CandidateUserRead
    election_posts: list[CandidatePostRead]


class CandidateElectionCreate(BaseSchema):
    post_ids: list[int]
