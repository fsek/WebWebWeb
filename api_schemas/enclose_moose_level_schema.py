from api_schemas.base_schema import BaseSchema
from datetime import datetime, date
from zoneinfo import ZoneInfo
from api_schemas.enclose_moose_submission_schema import EncloseMooseSubmissionRead


class EncloseMooseLevelInitialRead(BaseSchema):
    level_id: str
    release_date: date
    day_index: int | None
    name: str

    encoded_grid: str
    wall_budget: int

    player_submission: EncloseMooseSubmissionRead | None = None


class EncloseMooseLevelUnlockedRead(EncloseMooseLevelInitialRead):
    optimal_score: int
    optimal_solution: set[int]
    optimal_is_unique: bool | None

    score_distribution: dict[int, int]


class EncloseMooseLevelCreate(BaseSchema):
    level_id: str
    release_date: date = datetime.now(ZoneInfo("Europe/Stockholm")).date()
    day_index: int | None = None
    name: str

    encoded_grid: str
    wall_budget: int


class EncloseMooseLevelUpdate(BaseSchema):
    release_date: date | None = None
    day_index: int | None = None
    name: str | None = None

    encoded_grid: str | None = None
    wall_budget: int | None = None
