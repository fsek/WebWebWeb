from typing import TYPE_CHECKING

from db_models.book_category_model import BookCategory_DB
from helpers.constants import MAX_BOOK_USER, MAX_BOOK_TRANSACTION, MAX_BOOK_TITLE
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional
from sqlalchemy import ForeignKey, String


if TYPE_CHECKING:
    from .book_category_model import BookCategory_DB


class Book_DB(BaseModel_DB):
    __tablename__ = "book_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title: Mapped[str] = mapped_column(String(MAX_BOOK_TITLE))

    user: Mapped[Optional[str]] = mapped_column(String(MAX_BOOK_USER), default=None)

    transaction: Mapped[Optional[str]] = mapped_column(String(MAX_BOOK_TRANSACTION))

    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bookcategory_table.id"), default=None)

    category: Mapped[Optional["BookCategory_DB"]] = relationship(back_populates="books", init=False)

    price: Mapped[int] = mapped_column(default=0)

    pass
