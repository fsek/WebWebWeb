from api_schemas.base_schema import BaseSchema
from api_schemas.img_schema import ImgInAlbum
from helpers.types import datetime_utc


from api_schemas.user_schemas import SimpleUserRead


class AlbumCreate(BaseSchema):
    title_sv: str
    title_en: str
    desc_sv: str
    desc_en: str
    year: int
    location: str
    date: datetime_utc


class AlbumRead(BaseSchema):
    id: int
    title_sv: str
    title_en: str
    desc_sv: str
    desc_en: str
    year: int
    date: datetime_utc
    location: str
    photographer: SimpleUserRead | None
    imgs: list[ImgInAlbum]


class AlbumPhotographerAdd(BaseSchema):
    user_id: int
    album_id: int
