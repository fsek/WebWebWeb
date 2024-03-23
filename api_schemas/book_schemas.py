from api_schemas.base_schema import BaseSchema
from api_schemas.book_category_schemas import BookCategoryRead


class BookRead(BaseSchema):
    id: int
    title: str
    user: str
    transaction: str
    category: BookCategoryRead | None
    price: int | None


class BookCreate(BaseSchema):
    title: str
    user: str | None
    transaction: str
    category: BookCategoryRead
    price: int
