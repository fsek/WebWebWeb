from helpers.types import datetime_utc
from db_models.candidate_model import Candidate_DB
from db_models.candidate_post_model import Candidation_DB
from db_models.election_post_model import ElectionPost_DB
from db_models.post_model import Post_DB
from helpers.constants import MAX_SUB_ELECTION_TITLE
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy


if TYPE_CHECKING:
    from .candidate_model import Candidate_DB
    from db_models.election_post_model import ElectionPost_DB
    from db_models.post_model import Post_DB
    from db_models.election_model import Election_DB
    from db_models.nomination_model import Nomination_DB


class SubElection_DB(BaseModel_DB):
    __tablename__ = "sub_election_table"

    sub_election_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title_sv: Mapped[str] = mapped_column(String(MAX_SUB_ELECTION_TITLE))

    title_en: Mapped[str] = mapped_column(String(MAX_SUB_ELECTION_TITLE))

    end_time: Mapped[datetime_utc] = mapped_column()

    election_posts: Mapped[list["ElectionPost_DB"]] = relationship(
        back_populates="sub_election", cascade="all, delete-orphan"
    )

    election_id: Mapped[int] = mapped_column(ForeignKey("election_table.election_id"))

    election: Mapped["Election_DB"] = relationship(back_populates="sub_elections", init=False)

    candidates: Mapped[list["Candidate_DB"]] = relationship(
        back_populates="sub_election", cascade="all, delete-orphan", init=False
    )

    nominations: Mapped[list["Nomination_DB"]] = relationship(
        back_populates="sub_election", cascade="all, delete-orphan", init=False
    )

    # We need this because we sometimes want to not show what candidate made a candidation
    candidations: Mapped[list["Candidation_DB"]] = relationship(
        back_populates="sub_election", cascade="all, delete-orphan", init=False
    )

    posts: AssociationProxy[list["Post_DB"]] = association_proxy(
        target_collection="election_posts", attr="post", init=False
    )
