from api_schemas.base_schema import BaseSchema
from api_schemas.candidate_schema import CandidateElectionRead, CandidatePostRead
from helpers.types import datetime_utc


class ElectionPostRead(BaseSchema):
    id: int
    name: str
    council_id: int


class ElectionRead(BaseSchema):
    election_id: int
    title_sv: str
    title_en: str
    start_time: datetime_utc
    end_time_guild_meeting: datetime_utc | None
    end_time_middle_meeting: datetime_utc | None
    end_time_all: datetime_utc
    description_sv: str | None
    description_en: str | None
    posts: list[ElectionPostRead]
    candidates: list[CandidateElectionRead]


class ElectionMemberRead(BaseSchema):
    election_id: int
    title_sv: str
    title_en: str
    start_time: datetime_utc
    end_time_guild_meeting: datetime_utc | None
    end_time_middle_meeting: datetime_utc | None
    end_time_all: datetime_utc
    description_sv: str | None
    description_en: str | None
    posts: list[ElectionPostRead]
    candidations: list[CandidatePostRead]


class ElectionCreate(BaseSchema):
    title_sv: str
    title_en: str
    start_time: datetime_utc
    end_time_guild_meeting: datetime_utc | None
    end_time_middle_meeting: datetime_utc | None
    end_time_all: datetime_utc
    description_sv: str | None
    description_en: str | None


class ElectionUpdate(BaseSchema):
    title_sv: str | None
    title_en: str | None
    start_time: datetime_utc | None
    end_time_guild_meeting: datetime_utc | None
    end_time_middle_meeting: datetime_utc | None
    end_time_all: datetime_utc | None
    description_sv: str | None
    description_en: str | None


class ElectionPostCreate(BaseSchema):
    post_id: int
    description: str | None = None


class ElectionAddPosts(BaseSchema):
    posts: list[ElectionPostCreate]
