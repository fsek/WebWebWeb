from api_schemas.base_schema import BaseSchema
from api_schemas.img_schema import ImgInAlbum
from helpers.types import datetime_utc


class AlbumCreate(BaseSchema):
    name: str
    year: int
    location: str
    date: datetime_utc


class AlbumRead(BaseSchema):
    id: int
    name: str
    year: int
    date: datetime_utc
    location: str
    imgs: list[ImgInAlbum]
