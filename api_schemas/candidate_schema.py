from api_schemas.base_schema import BaseSchema


class _PostRead(BaseSchema):
    id: int
    name: str
    council_id: int


class CandidateRead(BaseSchema):
    candidate_id: int
    post: list[_PostRead]
    election_id: int
    user_id: int
