from helpers.constants import MAX_SPECIALISATION_DESC, MAX_SPECIALISATION_TITLE
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

if TYPE_CHECKING:
    from .associated_img_model import AssociatedImg_DB
    from .program_model import Program_DB
    from .specialisation_course_model import SpecialisationCourse_DB
    from .course_model import Course_DB


class Specialisation_DB(BaseModel_DB):
    __tablename__ = "specialisation_table"

    specialisation_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title_sv: Mapped[str] = mapped_column(String(MAX_SPECIALISATION_TITLE))

    title_en: Mapped[str] = mapped_column(String(MAX_SPECIALISATION_TITLE))

    program_id: Mapped[int] = mapped_column(ForeignKey("program_table.program_id"))

    program: Mapped["Program_DB"] = relationship(back_populates="specialisations", init=False)

    description_sv: Mapped[Optional[str]] = mapped_column(String(MAX_SPECIALISATION_DESC), default=None)

    description_en: Mapped[Optional[str]] = mapped_column(String(MAX_SPECIALISATION_DESC), default=None)

    associated_img_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("associated_img_table.associated_img_id"), default=None
    )

    associated_img: Mapped[Optional["AssociatedImg_DB"]] = relationship(
        back_populates="specialisation", init=False, uselist=False
    )

    specialisation_courses: Mapped[list["SpecialisationCourse_DB"]] = relationship(
        back_populates="specialisation", cascade="all, delete-orphan", init=False
    )
    courses: AssociationProxy[list["Course_DB"]] = association_proxy(
        target_collection="specialisation_courses", attr="course", init=False
    )
