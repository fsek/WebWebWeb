from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey

if TYPE_CHECKING:
    from .specialisation_model import Specialisation_DB
    from .course_model import Course_DB


class SpecialisationCourse_DB(BaseModel_DB):
    __tablename__ = "specialisation_course_table"

    specialisation_id: Mapped[int] = mapped_column(
        ForeignKey("specialisation_table.specialisation_id"), primary_key=True
    )
    course_id: Mapped[int] = mapped_column(ForeignKey("course_table.course_id"), primary_key=True)

    specialisation: Mapped["Specialisation_DB"] = relationship(back_populates="specialisation_courses", init=False)
    course: Mapped["Course_DB"] = relationship(back_populates="specialisation_courses", init=False)
