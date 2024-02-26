from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    Mapped,
    mapped_column,
    relationship,
)


class BaseModel_DB(DeclarativeBase, MappedAsDataclass):
    pass


class User_DB(BaseModel_DB):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column()

    books: Mapped[list["Book_DB"]] = relationship(back_populates="user", init=False)


class Book_DB(BaseModel_DB):
    __tablename__ = "book_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title: Mapped[str] = mapped_column()

    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user_table.id"), default=None
    )

    user: Mapped[Optional["User_DB"]] = relationship(
        back_populates="books", init=False
    )