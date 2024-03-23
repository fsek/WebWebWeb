from typing import Annotated

from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_BOOK_AUTHOR, MAX_BOOK_TITLE

class AdRead(BaseSchema):
    ad_id: int
    title: str
    author: str | None
    price: int | None
    course: str | None
    author: str | None
    seller: str
    selling: bool
    condition: int
    
    
class AdCreate(BaseSchema):
    title: str
    author: str | None
    price: int | None
    course: str | None
    author: str | None
    seller: str
    selling: bool
    condition: int
    
class AdUpdate(BaseSchema):
    title: Annotated[str, StringConstraints(max_length=MAX_BOOK_TITLE)] | None = None
    author: Annotated[str, StringConstraints(max_length=MAX_BOOK_AUTHOR)] | None = None
    price: int | None = None
    course: Annotated[str, StringConstraints(max_length=MAX_BOOK_TITLE)] | None = None
    selling: bool | None = None
    condition: int | None = None
