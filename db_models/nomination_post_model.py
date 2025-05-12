from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from db_models.election_post_model import ElectionPost_DB
    from db_models.nomination_model import Nominee_DB


class Nomination_DB(BaseModel_DB):
    __tablename__ = "nomination_table"

    nominee_id: Mapped[int] = mapped_column(ForeignKey("nominee_table.nominee_id"), primary_key=True)
    election_post_id: Mapped[int] = mapped_column(ForeignKey("election_post_table.election_post_id"), primary_key=True)

    nominee: Mapped["Nominee_DB"] = relationship(back_populates="nominations", init=False)
    election_post: Mapped["ElectionPost_DB"] = relationship(back_populates="nominations", init=False)
