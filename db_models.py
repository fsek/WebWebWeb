from typing import Optional
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


association_table = Table(
    "tecaher_student_association",
    BaseModelDB.metadata,
    Column("teacher_id", ForeignKey("teacher_table.id"), primary_key=True),
    Column("student_id", ForeignKey("student_table.id"), primary_key=True),
)


# name, age, password, int
class Student_DB(BaseModelDB):
    __tablename__ = "student_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    year: Mapped[int] = mapped_column()

    card_pin: Mapped[int] = mapped_column()

    books: Mapped[list["Book_DB"]] = relationship(back_populates="student", init=False)

    teacher: Mapped[list["Teacher_DB"]] = relationship(
        back_populates="student", init=False, secondary=association_table
    )


class Teacher_DB(BaseModelDB):
    __tablename__ = "teacher_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column()

    student: Mapped[list["Student_DB"]] = relationship(
        back_populates="teacher", init=False, secondary=association_table
    )


class Book_DB(BaseModelDB):
    __tablename__ = "book_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    consumed_by_dog: Mapped[bool] = mapped_column()

    student_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("student_table.id"), init=False
    )

    student: Mapped[Optional["Student_DB"]] = relationship(
        back_populates="books", init=False
    )
