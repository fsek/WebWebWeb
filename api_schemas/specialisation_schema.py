from typing import Annotated, TYPE_CHECKING
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_SPECIALISATION_DESC, MAX_SPECIALISATION_TITLE

if TYPE_CHECKING:
    from api_schemas.program_schema import SimpleProgramRead
    from api_schemas.course_schema import SimpleCourseRead


class SpecialisationRead(BaseSchema):
    specialisation_id: int
    title_sv: str
    title_en: str
    programs: list["SimpleProgramRead"] = []
    description_sv: str | None
    description_en: str | None
    associated_img_id: int | None
    courses: list["SimpleCourseRead"] = []


class SpecialisationCreate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_TITLE)]
    title_en: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_TITLE)]
    program_ids: list[int] = []
    description_sv: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_DESC)] | None = None


class SpecialisationUpdate(BaseSchema):
    title_sv: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_TITLE)]
    title_en: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_TITLE)]
    program_ids: list[int] = []
    description_sv: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_SPECIALISATION_DESC)] | None = None
