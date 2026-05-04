from typing import Annotated
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from api_schemas.course_document_schema import CourseDocumentRead
from api_schemas.program_year_schema import SimpleProgramYearRead
from api_schemas.specialisation_schema import SimpleSpecialisationRead
from helpers.constants import MAX_COURSE_CODE, MAX_COURSE_DESC, MAX_COURSE_TITLE
from helpers.types import datetime_utc


class SimpleCourseRead(BaseSchema):
    course_id: int
    title: str
    course_code: str | None
    short_identifier: str | None  # Kept so we can search for it


class CourseRead(BaseSchema):
    course_id: int
    title: str
    course_code: str | None
    short_identifier: str | None
    description: str | None
    associated_img_id: int | None
    documents: list[CourseDocumentRead] = []
    updated_at: datetime_utc
    program_years: list[SimpleProgramYearRead] = []
    specialisations: list[SimpleSpecialisationRead] = []


class CourseCreate(BaseSchema):
    title: Annotated[str, StringConstraints(max_length=MAX_COURSE_TITLE)]
    course_code: Annotated[str, StringConstraints(max_length=MAX_COURSE_CODE)]
    short_identifier: Annotated[str, StringConstraints(max_length=MAX_COURSE_TITLE)] | None = None
    description: Annotated[str, StringConstraints(max_length=MAX_COURSE_DESC)] | None = None


class CourseUpdate(BaseSchema):
    title: Annotated[str, StringConstraints(max_length=MAX_COURSE_TITLE)]
    course_code: Annotated[str, StringConstraints(max_length=MAX_COURSE_CODE)]
    short_identifier: Annotated[str, StringConstraints(max_length=MAX_COURSE_TITLE)] | None = None
    description: Annotated[str, StringConstraints(max_length=MAX_COURSE_DESC)] | None = None
