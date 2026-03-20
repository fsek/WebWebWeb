from helpers.constants import MAX_COURSE_TITLE, MAX_COURSE_DESC, MAX_COURSE_CODE
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

if TYPE_CHECKING:
    from .associated_img_model import AssociatedImg_DB
    from .program_year_model import ProgramYear_DB
    from .program_year_course_model import ProgramYearCourse_DB
    from .course_document_model import CourseDocument_DB
    from .specialisation_course_model import SpecialisationCourse_DB
    from .specialisation_model import Specialisation_DB


class Course_DB(BaseModel_DB):
    __tablename__ = "course_table"

    course_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title: Mapped[str] = mapped_column(String(MAX_COURSE_TITLE))

    course_code: Mapped[Optional[str]] = mapped_column(String(MAX_COURSE_CODE), default=None)

    description: Mapped[Optional[str]] = mapped_column(String(MAX_COURSE_DESC), default=None)

    program_year_courses: Mapped[list["ProgramYearCourse_DB"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", init=False
    )

    program_years: AssociationProxy[list["ProgramYear_DB"]] = association_proxy(
        target_collection="program_year_courses", attr="program_year", init=False
    )

    specialisation_courses: Mapped[list["SpecialisationCourse_DB"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", init=False
    )

    specialisations: AssociationProxy[list["Specialisation_DB"]] = association_proxy(
        target_collection="specialisation_courses", attr="specialisation", init=False
    )

    img_id: Mapped[Optional[int]] = mapped_column(ForeignKey("associated_img_table.associated_image_id"), default=None)

    img: Mapped[Optional["AssociatedImg_DB"]] = relationship(back_populates="course", init=False, uselist=False)

    documents: Mapped[list["CourseDocument_DB"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", init=False
    )
