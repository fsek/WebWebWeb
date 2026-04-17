from helpers.constants import MAX_PROGRAM_YEAR_DESC, MAX_PROGRAM_YEAR_TITLE
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

if TYPE_CHECKING:
    from .associated_img_model import AssociatedImg_DB
    from .program_model import Program_DB
    from .program_year_course_model import ProgramYearCourse_DB
    from .course_model import Course_DB


class ProgramYear_DB(BaseModel_DB):
    __tablename__ = "program_year_table"
    # See https://stackoverflow.com/questions/10059345/sqlalchemy-unique-across-multiple-columns
    # Ensures that program_year titles are unique within the same program, so we can fetch by title
    __table_args__ = (
        UniqueConstraint("program_id", "title_sv_urlized", name="uq_program_year_program_sv_urlized"),
        UniqueConstraint("program_id", "title_en_urlized", name="uq_program_year_program_en_urlized"),
    )

    program_year_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title_sv: Mapped[str] = mapped_column(String(MAX_PROGRAM_YEAR_TITLE))

    title_sv_urlized: Mapped[str] = mapped_column(String(MAX_PROGRAM_YEAR_TITLE))

    title_en: Mapped[str] = mapped_column(String(MAX_PROGRAM_YEAR_TITLE))

    title_en_urlized: Mapped[str] = mapped_column(String(MAX_PROGRAM_YEAR_TITLE))

    program_id: Mapped[int] = mapped_column(ForeignKey("program_table.program_id"))

    program: Mapped["Program_DB"] = relationship(back_populates="program_years", init=False)

    description_sv: Mapped[Optional[str]] = mapped_column(String(MAX_PROGRAM_YEAR_DESC), default=None)

    description_en: Mapped[Optional[str]] = mapped_column(String(MAX_PROGRAM_YEAR_DESC), default=None)

    associated_img_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("associated_img_table.associated_img_id"), default=None
    )

    associated_img: Mapped[Optional["AssociatedImg_DB"]] = relationship(
        back_populates="program_year", init=False, uselist=False
    )

    program_year_courses: Mapped[list["ProgramYearCourse_DB"]] = relationship(
        back_populates="program_year", cascade="all, delete-orphan", init=False
    )
    courses: AssociationProxy[list["Course_DB"]] = association_proxy(
        target_collection="program_year_courses", attr="course", init=False
    )
