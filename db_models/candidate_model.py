from db_models.election_model import Election_DB
from db_models.post_model import Post_DB
from helpers.constants import MAX_CANDIDATE_DESC
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, String

if TYPE_CHECKING:
    from .user_model import User_DB


class Candidate_DB(BaseModel_DB):
    __tablename__ = "candidate_table"

    candidate_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    post: Mapped["Post_DB"] = relationship("Post_DB", back_populates="candidates")

    description: Mapped[Optional[str]] = mapped_column(String(MAX_CANDIDATE_DESC))

    election_id: Mapped[int] = mapped_column(ForeignKey("election_table.id"))

    election: Mapped["Election_DB"] = relationship("Election_DB", back_populates="candidates", init=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))

    user: Mapped["User_DB"] = relationship("User_DB", back_populates="candidates", init=False)
    pass
