from api_schemas.base_schema import BaseSchema


class PostRead(BaseSchema):
    post_id: int


class CandidateRead(BaseSchema):
    candidate_id: int
    election_id: int
    user_id: int
    posts: list[PostRead]


class CandidateElectionRead(BaseSchema):
    candidate_id: int
    user_id: int
    posts: list[PostRead]
