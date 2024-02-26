from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, Mapped, mapped_column


class BaseModel_DB(DeclarativeBase, MappedAsDataclass):
    pass


class Book_DB(BaseModel_DB):
    __tablename__ = "book_table"

    # Integer value, makred as primary key. Every table need one primary key column.
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    # String value, max length 200
    title: Mapped[str] = mapped_column(String(200))

    # Integer column
    page_count: Mapped[int] = mapped_column()

    # Float column
    rating: Mapped[float] = mapped_column()

    # Optional (Nullable) string column. Instances of Book_DB will have a summary type of str or None.
    summary: Mapped[Optional[str]] = mapped_column(default=None)

    # A default value can be provided.
    read_times: Mapped[int] = mapped_column(default=0)