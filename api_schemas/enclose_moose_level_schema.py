from api_schemas.base_schema import BaseSchema
from datetime import datetime, date, UTC


class EncloseMooseLevelRead(BaseSchema):
    level_id: str
    release_date: date
    day_index: int | None
    name: str

    encoded_grid: str
    wall_budget: int

    optimal_score: int
    optimal_solution: set[int]  # Could consider not showing optimal_solution until player has submitted
    optimal_is_unique: bool | None


class EncloseMooseLevelCreate(BaseSchema):
    level_id: str
    release_date: date = datetime.now(UTC).date()
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
