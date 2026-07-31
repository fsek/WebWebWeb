from api_schemas.base_schema import BaseSchema
from helpers.types import datetime


class EncloseMooseSubmissionRead(BaseSchema):
    level_id: str
    submission_time: datetime

    player_id: int
    player_score: int
    player_solution: set[int]


class EncloseMooseSubmissionCreate(BaseSchema):
    player_solution: set[int]
