from pydantic import Field, model_validator
from datetime import datetime, date
from zoneinfo import ZoneInfo
from api_schemas.base_schema import BaseSchema
from api_schemas.enclose_moose_submission_schema import EncloseMooseSubmissionRead


class EncloseMooseLevelRead(BaseSchema):
    level_id: int
    release_date: date
    day_index: int | None
    name_sv: str
    name_en: str

    encoded_grid: str
    wall_budget: int

    show_spoilers: bool = Field(default=False, exclude=True)

    optimal_score: int | None = None
    optimal_solution: set[int] | None = None
    optimal_is_unique: bool | None = None

    player_submission: EncloseMooseSubmissionRead | None = None
    score_distribution: dict[int, int] | None = None

    @model_validator(mode="after")
    def redact_spoilers(self):
        if not self.show_spoilers:
            self.optimal_score = None
            self.optimal_solution = None
            self.optimal_is_unique = None
            self.score_distribution = None

        return self


class EncloseMooseLevelCreate(BaseSchema):
    release_date: date = Field(default_factory=lambda: datetime.now(ZoneInfo("Europe/Stockholm")).date())
    day_index: int | None = None
    name_sv: str
    name_en: str

    encoded_grid: str
    wall_budget: int


class EncloseMooseLevelUpdate(BaseSchema):
    release_date: date | None = None
    day_index: int | None = None
    name_sv: str | None = None
    name_en: str | None = None

    encoded_grid: str | None = None
    wall_budget: int | None = None
