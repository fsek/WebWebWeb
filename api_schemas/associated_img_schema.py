from fastapi import UploadFile
from api_schemas.base_schema import BaseSchema


class AssociatedImgRead(BaseSchema):
    associated_image_id: int
    path: str


class AssociatedImgCreate(BaseSchema):
    file: UploadFile
