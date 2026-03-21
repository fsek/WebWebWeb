from typing import Annotated
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from api_schemas.course_document_schema import CourseDocumentRead
from api_schemas.program_year_schema import ProgramYearRead
from api_schemas.specialisation_schema import SpecialisationRead
from helpers.constants import MAX_COURSE_CODE, MAX_COURSE_DESC, MAX_COURSE_TITLE
from helpers.types import datetime_utc
from fastapi import UploadFile


class SimpleCourseRead(BaseSchema):
    course_id: int
    title: str
    course_code: str | None


class CourseRead(BaseSchema):
    course_id: int
    title: str
    course_code: str | None
    description: str | None
    img_id: int | None
    documents: list[CourseDocumentRead] = []
    updated_at: datetime_utc
    program_years: list[ProgramYearRead] = []
    specialisations: list[SpecialisationRead] = []


class CourseCreate(BaseSchema):
    title: Annotated[str, StringConstraints(max_length=MAX_COURSE_TITLE)]
    course_code: Annotated[str, StringConstraints(max_length=MAX_COURSE_CODE)] | None = None
    description: Annotated[str, StringConstraints(max_length=MAX_COURSE_DESC)] | None = None
    img_file: UploadFile | None = None
    program_year_ids: list[int] = []
    specialisation_ids: list[int] = []


class CourseUpdate(BaseSchema):
    title: Annotated[str, StringConstraints(max_length=MAX_COURSE_TITLE)] | None = None
    course_code: Annotated[str, StringConstraints(max_length=MAX_COURSE_CODE)] | None = None
    description: Annotated[str, StringConstraints(max_length=MAX_COURSE_DESC)] | None = None
    img_file: UploadFile | None = None
    program_year_ids: list[int] | None = None
    specialisation_ids: list[int] | None = None
