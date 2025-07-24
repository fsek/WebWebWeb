from helpers.db_util import created_at_column
from helpers.types import datetime_utc

from sqlalchemy import ForeignKey, String
from db_models.base_model import BaseModel_DB
from typing import TYPE_CHECKING

from helpers.constants import MAX_ADVENTURE_MISSION_DESC, MAX_ADVENTURE_MISSION_NAME
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .group_mission_model import GroupMission_DB

if TYPE_CHECKING:
    from .nollning_model import Nollning_DB


class AdventureMission_DB(BaseModel_DB):
    __tablename__ = "adventure_mission_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    nollning_id: Mapped[int] = mapped_column(ForeignKey("nollning_table.id"))

    nollning: Mapped["Nollning_DB"] = relationship(back_populates="missions", init=False)

    nollning_week: Mapped[int] = mapped_column()

    title: Mapped[str] = mapped_column(String(MAX_ADVENTURE_MISSION_NAME))

    description: Mapped[str] = mapped_column(String(MAX_ADVENTURE_MISSION_DESC))

    max_points: Mapped[int] = mapped_column()

    min_points: Mapped[int] = mapped_column()

    group_missions: Mapped[list["GroupMission_DB"]] = relationship(
        back_populates="adventure_mission", cascade="all, delete-orphan", init=False
    )

    created_at: Mapped[datetime_utc] = created_at_column()
