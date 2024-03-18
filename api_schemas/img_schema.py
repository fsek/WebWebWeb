from api_schemas.base_schema import BaseSchema
from fastapi import UploadFile


class ImgCreate(BaseSchema):
    File: UploadFile
