from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey

if TYPE_CHECKING:
    from .program_year_model import ProgramYear_DB
    from .course_model import Course_DB


class ProgramYearCourse_DB(BaseModel_DB):
    __tablename__ = "program_year_course_table"

    program_year_id: Mapped[int] = mapped_column(ForeignKey("program_year_table.program_year_id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course_table.course_id"), primary_key=True)

    program_year: Mapped["ProgramYear_DB"] = relationship(back_populates="program_year_courses", init=False)
    course: Mapped["Course_DB"] = relationship(back_populates="program_year_courses", init=False)
