from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import ForeignKey, JSON
from typing import TYPE_CHECKING
from helpers.types import datetime_utc

if TYPE_CHECKING:
    from db_models.enclose_moose_level_model import EncloseMooseLevel_DB


class EncloseMooseSubmission_DB(BaseModel_DB):
    __tablename__ = "enclose_moose_submission_table"

    level_id: Mapped[int] = mapped_column(
        ForeignKey("enclose_moose_level_table.level_id", ondelete="CASCADE"),
        primary_key=True,
    )
    submission_time: Mapped[datetime_utc] = mapped_column()

    player_id: Mapped[int] = mapped_column(
        ForeignKey("user_table.id", ondelete="CASCADE"),
        primary_key=True,
    )
    player_score: Mapped[int] = mapped_column()
    player_solution: Mapped[list[int]] = mapped_column(JSON)

    level: Mapped["EncloseMooseLevel_DB"] = relationship(back_populates="submissions", init=False, viewonly=True)
