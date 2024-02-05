from api_schemas.base_schema import BaseSchema


class SongCategoryRead(BaseSchema):
    id: int | None
    name: str


class SongCategoryCreate(BaseSchema):
    name: str
