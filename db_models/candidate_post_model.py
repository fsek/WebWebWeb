from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from db_models.election_post_model import ElectionPost_DB
    from db_models.candidate_model import Candidate_DB
    from db_models.election_model import Election_DB


class Candidation_DB(BaseModel_DB):
    __tablename__ = "candidations_table"

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidate_table.candidate_id"), primary_key=True)
    election_post_id: Mapped[int] = mapped_column(ForeignKey("election_post_table.election_post_id"), primary_key=True)

    candidate: Mapped["Candidate_DB"] = relationship(back_populates="candidations", init=False)
    election_post: Mapped["ElectionPost_DB"] = relationship(back_populates="candidations", init=False)

    # We need to save the election here because we sometimes want to not show what candidate made a candidation
    election_id: Mapped[int] = mapped_column(ForeignKey("election_table.election_id"))

    election: Mapped["Election_DB"] = relationship(back_populates="candidations", init=False)
