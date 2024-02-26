from sqlalchemy import Column, ForeignKey, Table

from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    Mapped,
    mapped_column,
    relationship,
)


class BaseModel_DB(DeclarativeBase, MappedAsDataclass):
    pass


association_table = Table(
    "parent_child_association",
    BaseModel_DB.metadata,
    Column("parent_id", ForeignKey("parent_table.id"), primary_key=True),
    Column("child_id", ForeignKey("child_table.id"), primary_key=True),
)


class Parent_DB(BaseModel_DB):
    __tablename__ = "parent_table"

    name: Mapped[str] = mapped_column()
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    children: Mapped[list["Child_DB"]] = relationship(
        back_populates="parents", init=False, secondary=association_table
    )


class Child_DB(BaseModel_DB):
    __tablename__ = "child_table"

    age: Mapped[int] = mapped_column()
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    parents: Mapped[list[Parent_DB]] = relationship(
        back_populates="children", init=False, secondary=association_table
    )