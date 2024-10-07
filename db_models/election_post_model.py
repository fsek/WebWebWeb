from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String
from db_models.candidate_post_model import CandidatePost_DB
from helpers.constants import MAX_ELECTION_DESC
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from post_model import Post_DB
    from db_models.election_model import Election_DB


class ElectionPost_DB(BaseModel_DB):
    __tablename__ = "election_post_table"

    election_post_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    election_id: Mapped[int] = mapped_column(ForeignKey("election_table.election_id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("post_table.id"))

    post: Mapped["Post_DB"] = relationship(back_populates="election_posts", init=False)
    election: Mapped["Election_DB"] = relationship(back_populates="election_posts", init=False)

    candidate_posts: Mapped[list["CandidatePost_DB"]] = relationship(back_populates="election_post", init=False)

    description: Mapped[Optional[str]] = mapped_column(String(MAX_ELECTION_DESC), default=None)
