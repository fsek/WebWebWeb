from api_schemas.base_schema import BaseSchema
from api_schemas.candidate_schema import CandidateElectionRead
from helpers.types import datetime_utc


class ElectionPostRead(BaseSchema):
    id: int
    name: str
    council_id: int


class ElectionRead(BaseSchema):
    election_id: int
    title: str
    start_time: datetime_utc
    end_time: datetime_utc
    description: str | None
    posts: list[ElectionPostRead]
    candidates: list[CandidateElectionRead]


class ElectionCreate(BaseSchema):
    title: str
    start_time: datetime_utc
    end_time: datetime_utc
    description: str


class ElectionPostCreate(BaseSchema):
    post_id: int
    description: str | None = None


class ElectionAddPosts(BaseSchema):
    posts: list[ElectionPostCreate]
