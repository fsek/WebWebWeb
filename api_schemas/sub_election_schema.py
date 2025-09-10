from api_schemas.base_schema import BaseSchema
from api_schemas.candidate_schema import CandidateRead, CandidatePostRead
from helpers.types import datetime_utc


class ElectionPostRead(BaseSchema):
    election_post_id: int
    post_id: int
    name_sv: str
    name_en: str
    elected_at_semester: str | None
    elected_by: str | None
    elected_user_recommended_limit: int
    elected_user_max_limit: int
    council_id: int
    candidation_count: int


class SubElectionMemberRead(BaseSchema):
    sub_election_id: int
    election_id: int
    title_sv: str
    title_en: str
    end_time: datetime_utc
    election_posts: list[ElectionPostRead]


class SubElectionRead(SubElectionMemberRead):
    candidates: list[CandidateRead]


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


class MovePostRequest(BaseSchema):
    election_post_id: int
    new_sub_election_id: int
