from typing import Annotated
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from api_schemas.course_schema import CourseRead
from helpers.constants import MAX_SPECIALISATION_DESC, MAX_SPECIALISATION_TITLE


class SpecialisationRead(BaseSchema):
    specialisation_id: int
    title_sv: str
    title_en: str
    program_id: int
    description_sv: str | None
    description_en: str | None
    img_id: int | None
    courses: list[CourseRead] = []


class SpecialisationCreate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_TITLE)]
    title_en: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_TITLE)]
    program_id: int
    description_sv: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_DESC)] | None = None


class SpecialisationUpdate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_TITLE)]
    title_en: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_TITLE)]
    program_id: int
    description_sv: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_DESC)] | None = None
