from api_schemas.base_schema import BaseSchema
from db_models.img_model import Img_DB


class AlbumCreate(BaseSchema):
    name: str


class AlbumRead(BaseSchema):
    id: int
    name: str
    imgs: list[Img_DB]
