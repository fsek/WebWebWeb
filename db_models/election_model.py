from helpers.types import datetime_utc
from helpers.constants import MAX_ELECTION_DESC, MAX_ELECTION_TITLE
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional
from sqlalchemy import String
from db_models.sub_election_model import SubElection_DB


class Election_DB(BaseModel_DB):
    __tablename__ = "election_table"

    election_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title_sv: Mapped[str] = mapped_column(String(MAX_ELECTION_TITLE))

    title_en: Mapped[str] = mapped_column(String(MAX_ELECTION_TITLE))

    start_time: Mapped[datetime_utc] = mapped_column()

    visible: Mapped[bool] = mapped_column(default=False)

    description_sv: Mapped[Optional[str]] = mapped_column(String(MAX_ELECTION_DESC), default=None)

    description_en: Mapped[Optional[str]] = mapped_column(String(MAX_ELECTION_DESC), default=None)

    sub_elections: Mapped[Optional[list["SubElection_DB"]]] = relationship(
        back_populates="election", cascade="all, delete-orphan", init=False
    )
