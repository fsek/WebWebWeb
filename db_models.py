from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    mapped_column,
    Mapped,
    relationship,
)


class BaseModelDB(DeclarativeBase, MappedAsDataclass):
    pass


# name, age, password, int
class UserInDB(BaseModelDB):
    __tablename__ = "user_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str] = mapped_column()


class BookInDB(BaseModelDB):
    __tablename__ = "book_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str] = mapped_column(String(50))
