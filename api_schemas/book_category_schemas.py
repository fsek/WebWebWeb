from api_schemas.base_schema import BaseSchema


class BookCategoryRead(BaseSchema):
    id: int | None
    name: str


class BookCategoryCreate(BaseSchema):
    name: str
