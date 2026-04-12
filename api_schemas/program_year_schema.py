from typing import Annotated, TYPE_CHECKING
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_PROGRAM_YEAR_DESC, MAX_PROGRAM_YEAR_TITLE

if TYPE_CHECKING:
    from api_schemas.course_schema import CourseRead


class ProgramYearRead(BaseSchema):
    program_year_id: int
    title_sv: str
    title_en: str
    program_id: int
    description_sv: str | None
    description_en: str | None
    img_id: int | None
    courses: list["CourseRead"] = []


class ProgramYearCreate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_YEAR_TITLE)]
    title_en: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_YEAR_TITLE)]
    program_id: int
    description_sv: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_YEAR_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_YEAR_DESC)] | None = None


class ProgramYearUpdate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_YEAR_TITLE)]
    title_en: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_YEAR_TITLE)]
    program_id: int
    description_sv: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_YEAR_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_YEAR_DESC)] | None = None
