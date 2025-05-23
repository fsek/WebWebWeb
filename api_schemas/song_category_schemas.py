from api_schemas.base_schema import BaseSchema


class SongCategoryRead(BaseSchema):
    id: int
    name: str


class SongCategoryCreate(BaseSchema):
    name: str
