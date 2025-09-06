from api_schemas.base_schema import BaseSchema
from api_schemas.candidate_schema import CandidateRead, CandidatePostRead
from helpers.types import datetime_utc


class ElectionPostRead(BaseSchema):
    id: int
    name_sv: str
    name_en: str
    council_id: int


class BaseSubElectionRead(BaseSchema):
    sub_election_id: int
    title_sv: str
    title_en: str
    end_time: datetime_utc
    posts: list[ElectionPostRead]


class SubElectionRead(BaseSubElectionRead):
    candidates: list[CandidateRead]


class SubElectionMemberRead(BaseSubElectionRead):
    candidations: list[CandidatePostRead]


class SubElectionCreate(BaseSchema):
    election_id: int
    title_sv: str
    title_en: str
    end_time: datetime_utc
    post_ids: list[int] | None = None


class SubElectionUpdate(BaseSchema):
    title_sv: str | None = None
    title_en: str | None = None
    end_time: datetime_utc | None = None
    post_ids: list[int] | None = None
