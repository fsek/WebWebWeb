from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from db_models.candidate_post_model import Candidation_DB
from db_models.nomination_model import Nomination_DB
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from post_model import Post_DB
    from db_models.sub_election_model import SubElection_DB


class ElectionPost_DB(BaseModel_DB):
    __tablename__ = "election_post_table"

    election_post_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    sub_election_id: Mapped[int] = mapped_column(ForeignKey("sub_election_table.sub_election_id"), init=False)
    sub_election: Mapped["SubElection_DB"] = relationship(back_populates="election_posts", init=False)

    post_id: Mapped[int] = mapped_column(ForeignKey("post_table.id"))
    post: Mapped["Post_DB"] = relationship(back_populates="election_posts", init=False)

    candidations: Mapped[list["Candidation_DB"]] = relationship(
        back_populates="election_post", cascade="all, delete-orphan", init=False
    )

    nominations: Mapped[list["Nomination_DB"]] = relationship(
        back_populates="election_post", cascade="all, delete-orphan", init=False
    )
