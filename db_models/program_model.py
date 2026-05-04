from helpers.constants import MAX_PROGRAM_DESC, MAX_PROGRAM_TITLE
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String

if TYPE_CHECKING:
    from .associated_img_model import AssociatedImg_DB
    from .program_year_model import ProgramYear_DB
    from .specialisation_model import Specialisation_DB
    from .program_specialisation_model import ProgramSpecialisation_DB


class Program_DB(BaseModel_DB):
    __tablename__ = "program_table"

    program_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title_sv: Mapped[str] = mapped_column(String(MAX_PROGRAM_TITLE))

    title_sv_urlized: Mapped[str] = mapped_column(String(MAX_PROGRAM_TITLE), unique=True)

    title_en: Mapped[str] = mapped_column(String(MAX_PROGRAM_TITLE))

    title_en_urlized: Mapped[str] = mapped_column(String(MAX_PROGRAM_TITLE), unique=True)

    description_sv: Mapped[Optional[str]] = mapped_column(String(MAX_PROGRAM_DESC), default=None)

    description_en: Mapped[Optional[str]] = mapped_column(String(MAX_PROGRAM_DESC), default=None)

    associated_img_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("associated_img_table.associated_img_id"), default=None
    )

    associated_img: Mapped[Optional["AssociatedImg_DB"]] = relationship(
        back_populates="program", init=False, uselist=False
    )

    program_years: Mapped[list["ProgramYear_DB"]] = relationship(
        back_populates="program", cascade="all, delete-orphan", init=False
    )

    program_specialisations: Mapped[list["ProgramSpecialisation_DB"]] = relationship(
        back_populates="program", cascade="all, delete-orphan", init=False
    )
    specialisations: AssociationProxy[list["Specialisation_DB"]] = association_proxy(
        target_collection="program_specialisations", attr="specialisation", init=False
    )
