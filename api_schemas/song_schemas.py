from api_schemas.base_schema import BaseSchema
from api_schemas.song_category_schemas import SongCategoryRead


class SongRead(BaseSchema):
    id: int
    title: str
    author: str
    content: str
    category: SongCategoryRead | None
    views: int


class SongCreate(BaseSchema):
    title: str
    author: str
    content: str
    category: SongCategoryRead
