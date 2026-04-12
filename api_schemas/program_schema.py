from typing import Annotated
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_PROGRAM_DESC, MAX_PROGRAM_TITLE
from api_schemas.program_year_schema import ProgramYearRead
from api_schemas.specialisation_schema import SpecialisationRead
from api_schemas.course_schema import (
    CourseRead,
)  # pyright: ignore[reportUnusedImport] # This is not used but is needed for the model_rebuild calls below

ProgramYearRead.model_rebuild()
SpecialisationRead.model_rebuild()


class ProgramRead(BaseSchema):
    program_id: int
    title_sv: str
    title_en: str
    description_sv: str | None
    description_en: str | None
    img_id: int | None
    program_years: list[ProgramYearRead] = []
    specialisations: list[SpecialisationRead] = []


class ProgramCreate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_TITLE)]
    title_en: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_TITLE)]
    description_sv: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_DESC)] | None = None


class ProgramUpdate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_TITLE)]
    title_en: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_TITLE)]
    description_sv: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_PROGRAM_DESC)] | None = None
