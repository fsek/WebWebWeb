from api_schemas.base_schema import BaseSchema
from api_schemas.candidate_schema import CandidateRead
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
    election_posts: list[ElectionPostRead]
    candidates: list[CandidateRead]


class ElectionCreate(BaseSchema):
    title: str
    start_time: datetime_utc
    end_time: datetime_utc
    description: str


class ElectionAddPosts(BaseSchema):
    posts: list[int]


# election_id: Mapped[int] = mapped_column(primary_key=True, init=False)

#     start_time: Mapped[datetime] = mapped_column()

#     end_time: Mapped[datetime] = mapped_column()

#     description: Mapped[Optional[str]] = mapped_column(String(MAX_ELECTION_DESC))

#     election_posts: Mapped[list["ElectionPost_DB"]] = relationship(
#         back_populates="elections", cascade="all, delete-orphan", init=False
#     )
#     candidates: Mapped[list["Candidate_DB"]] = relationship(
#         back_populates="elections", cascade="all, delete-orphan", init=False
#     )
