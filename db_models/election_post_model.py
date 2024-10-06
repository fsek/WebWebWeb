from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String
from helpers.constants import MAX_ELECTION_DESC
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from post_model import Post_DB
    from db_models.election_model import Election_DB


class ElectionPost_DB(BaseModel_DB):
    __tablename__ = "election_post_table"

    election_id: Mapped[int] = mapped_column(ForeignKey("election_table.election_id"), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("post_table.id"), primary_key=True)

    post: Mapped["Post_DB"] = relationship(back_populates="election_posts", init=False)
    election: Mapped["Election_DB"] = relationship(back_populates="election_posts", init=False)

    description: Mapped[Optional[str]] = mapped_column(String(MAX_ELECTION_DESC), default=None)
