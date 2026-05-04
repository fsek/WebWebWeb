from fastapi import UploadFile
from api_schemas.base_schema import BaseSchema


class AssociatedImgRead(BaseSchema):
    associated_img_id: int
    path: str


class AssociatedImgCreate(BaseSchema):
    file: UploadFile
    program_id: int | None = None
    program_year_id: int | None = None
    course_id: int | None = None
    specialisation_id: int | None = None
