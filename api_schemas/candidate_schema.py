from api_schemas.base_schema import BaseSchema
from api_schemas.user_schemas import UserRead


class PostRead(BaseSchema):
    post_id: int
    election_post_id: int


class CandidateRead(BaseSchema):
    candidate_id: int
    election_id: int
    user: UserRead
    election_posts: list[PostRead]


class CandidateElectionRead(BaseSchema):
    candidate_id: int
    user_id: int
    user: UserRead
    election_posts: list[PostRead]


class CandidateElectionCreate(BaseSchema):
    post_ids: list[int]
