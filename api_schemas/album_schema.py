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


class PhotographerInAlbumRead(BaseSchema):
    user: SimpleUserRead


class AlbumRead(BaseSchema):
    id: int
    title_sv: str
    title_en: str
    desc_sv: str
    desc_en: str
    year: int
    date: datetime_utc
    location: str
    photographer: list[PhotographerInAlbumRead]


class AlbumPhotographerAdd(BaseSchema):
    user_id: int
    album_id: int


class AlbumPatch(BaseSchema):
    title_sv: str | None = None
    title_en: str | None = None
    desc_sv: str | None = None
    desc_en: str | None = None
    location: str | None = None
