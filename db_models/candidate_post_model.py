from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey

from helpers.db_util import created_at_column
from helpers.types import datetime_utc
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from post_model import Post_DB
    from db_models.election_post_model import ElectionPost_DB
    from db_models.candidate_model import Candidate_DB
    from db_models.sub_election_model import SubElection_DB


class Candidation_DB(BaseModel_DB):
    __tablename__ = "candidations_table"

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidate_table.candidate_id"), primary_key=True)
    election_post_id: Mapped[int] = mapped_column(ForeignKey("election_post_table.election_post_id"), primary_key=True)

    candidate: Mapped["Candidate_DB"] = relationship(back_populates="candidations", init=False)
    election_post: Mapped["ElectionPost_DB"] = relationship(back_populates="candidations", init=False)

    sub_election_id: Mapped[int] = mapped_column(ForeignKey("sub_election_table.sub_election_id"))

    sub_election: Mapped["SubElection_DB"] = relationship(back_populates="candidations", init=False)

    post_id: Mapped[int] = mapped_column(ForeignKey("post_table.id"))
    post: Mapped["Post_DB"] = relationship(init=False)

    created_at: Mapped[datetime_utc] = created_at_column()
