from datetime import datetime
from db_models.candidate_model import Candidate_DB
from db_models.election_post_model import ElectionPost_DB
from helpers.constants import MAX_ELECTION_DESC
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String


class Election_DB(BaseModel_DB):
    __tablename__ = "election_table"

    election_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title: Mapped[str] = mapped_column()

    start_time: Mapped[datetime] = mapped_column()

    end_time: Mapped[datetime] = mapped_column()

    description: Mapped[Optional[str]] = mapped_column(String(MAX_ELECTION_DESC), default=None)

    election_posts: Mapped[list["ElectionPost_DB"]] = relationship(
        back_populates="elections", cascade="all, delete-orphan", init=False
    )
    candidates: Mapped[list["Candidate_DB"]] = relationship(
        back_populates="elections", cascade="all, delete-orphan", init=False
    )
