from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey


from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from post_model import Post_DB
    from db_models.candidate_model import Candidate_DB


class CandidatePost_DB(BaseModel_DB):
    __tablename__ = "candidate_post_table"

    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidate_table.candidate_id"), primary_key=True, init=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post_table.id"), primary_key=True, init=False)

    posts: Mapped["Post_DB"] = relationship(back_populates="candidate_posts", default=None)
    candidates: Mapped["Candidate_DB"] = relationship(back_populates="candidate_posts", default=None)
