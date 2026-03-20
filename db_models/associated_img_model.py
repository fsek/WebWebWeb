from typing import TYPE_CHECKING, Optional

from sqlalchemy import String

from helpers.constants import MAX_PATH_LENGTH
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column

if TYPE_CHECKING:
    from .program_model import Program_DB
    from .program_year_model import ProgramYear_DB
    from .course_model import Course_DB
    from .specialisation_model import Specialisation_DB


class AssociatedImg_DB(BaseModel_DB):
    __tablename__ = "associated_img_table"

    associated_image_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    path: Mapped[str] = mapped_column(String(MAX_PATH_LENGTH))

    program: Mapped[Optional["Program_DB"]] = relationship(back_populates="img", init=False, uselist=False)

    program_year: Mapped[Optional["ProgramYear_DB"]] = relationship(back_populates="img", init=False, uselist=False)

    course: Mapped[Optional["Course_DB"]] = relationship(back_populates="img", init=False, uselist=False)

    specialisation: Mapped[Optional["Specialisation_DB"]] = relationship(
        back_populates="img", init=False, uselist=False
    )
