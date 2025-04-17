from api_schemas.base_schema import BaseSchema
from api_schemas.img_schema import ImgInAlbum
from helpers.types import datetime_utc


class AlbumCreate(BaseSchema):
    name: str
    year: int


class AlbumRead(BaseSchema):
    id: int
    name: str
    year: int
    imgs: list[ImgInAlbum]
