from datetime import date
from helpers.constants import MAX_ENCLOSE_LEVEL_NAME, MAX_ENCLOSE_GRID
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Date, JSON

if TYPE_CHECKING:
    from db_models.enclose_moose_submission_model import EncloseMooseSubmission_DB


class EncloseMooseLevel_DB(BaseModel_DB):
    __tablename__ = "enclose_moose_level_table"

    level_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    release_date: Mapped[Optional[date]] = mapped_column(Date)
    day_index: Mapped[Optional[int]] = mapped_column()
    name_sv: Mapped[str] = mapped_column(String(MAX_ENCLOSE_LEVEL_NAME))
    name_en: Mapped[str] = mapped_column(String(MAX_ENCLOSE_LEVEL_NAME))

    encoded_grid: Mapped[str] = mapped_column(String(MAX_ENCLOSE_GRID))
    wall_budget: Mapped[int] = mapped_column()

    optimal_score: Mapped[int] = mapped_column()
    optimal_solution: Mapped[list[int]] = mapped_column(JSON)
    optimal_is_unique: Mapped[Optional[bool]] = mapped_column()

    submissions: Mapped[list["EncloseMooseSubmission_DB"]] = relationship(
        back_populates="level", cascade="all, delete-orphan", init=False
    )

    @property
    def score_distribution(self):
        score_distribution: dict[int, int] = {}
        for submission in self.submissions:
            score_distribution[submission.player_score] = score_distribution.get(submission.player_score, 0) + 1

        return score_distribution
