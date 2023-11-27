from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    Mapped,
    mapped_column,
    relationship,
)


class BaseModelDB(DeclarativeBase, MappedAsDataclass):
    pass


# TODO create association table. Check docs


class Parent_DB(BaseModelDB):
    __tablename__ = "parent_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column()

    # TODO relationship


class Child_DB(BaseModelDB):
    __tablename__ = "child_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    age: Mapped[int] = mapped_column()

    # TODO relationship
