from api_schemas.base_schema import BaseSchema
from api_schemas.sub_election_schema import SubElectionRead, SubElectionMemberRead
from helpers.types import datetime_utc, ELECTION_SEMESTERS


class BaseElectionRead(BaseSchema):
    election_id: int
    title_sv: str
    title_en: str
    start_time: datetime_utc
    description_sv: str | None
    description_en: str | None
    visible: bool


class ElectionRead(BaseElectionRead):
    sub_elections: list[SubElectionRead]


class ElectionMemberRead(BaseElectionRead):
    sub_elections: list[SubElectionMemberRead]


class ElectionCreate(BaseSchema):
    title_sv: str
    title_en: str
    start_time: datetime_utc
    description_sv: str | None
    description_en: str | None
    visible: bool = False


class ElectionUpdate(BaseSchema):
    title_sv: str | None
    title_en: str | None
    start_time: datetime_utc | None
    description_sv: str | None
    description_en: str | None
    visible: bool | None


class ElectionPopulate(BaseSchema):
    semester: ELECTION_SEMESTERS
    end_time_guild: datetime_utc
    end_time_board: datetime_utc
    end_time_board_intermediate: datetime_utc
    end_time_educational_council: datetime_utc
