from sqlalchemy import String
from typing import TYPE_CHECKING
from helpers.constants import MAX_BOOK_CATEGORY
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship

if TYPE_CHECKING:
    from db_models.book_model import Book_DB


class BookCategory_DB(BaseModel_DB):
    __tablename__ = "bookcategory_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column(String(MAX_BOOK_CATEGORY))

    books: Mapped[list["Book_DB"]] = relationship(back_populates="category", init=False)

    pass
