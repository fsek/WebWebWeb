from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey

if TYPE_CHECKING:
    from .specialisation_model import Specialisation_DB
    from .program_model import Program_DB


class ProgramSpecialisation_DB(BaseModel_DB):
    __tablename__ = "program_specialisation_table"

    program_id: Mapped[int] = mapped_column(ForeignKey("program_table.program_id"), primary_key=True)
    specialisation_id: Mapped[int] = mapped_column(
        ForeignKey("specialisation_table.specialisation_id"), primary_key=True
    )

    program: Mapped["Program_DB"] = relationship(back_populates="program_specialisations", init=False)
    specialisation: Mapped["Specialisation_DB"] = relationship(back_populates="program_specialisations", init=False)
