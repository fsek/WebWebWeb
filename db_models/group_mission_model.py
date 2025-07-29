from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING

from helpers.types import MISSION_CONFIRMED_TYPES
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from db_models.nollning_group_model import NollningGroup_DB
    from db_models.adventure_mission_model import AdventureMission_DB


class GroupMission_DB(BaseModel_DB):
    __tablename__ = "group_mission_table"

    points: Mapped[int] = mapped_column()

    adventure_mission_id: Mapped[int] = mapped_column(ForeignKey("adventure_mission_table.id"), primary_key=True)
    adventure_mission: Mapped["AdventureMission_DB"] = relationship(back_populates="group_missions", init=False)

    nollning_group_id: Mapped[int] = mapped_column(ForeignKey("nollning_group_table.id"), primary_key=True)
    nollning_group: Mapped["NollningGroup_DB"] = relationship(back_populates="group_missions", init=False)

    is_accepted: Mapped[MISSION_CONFIRMED_TYPES] = mapped_column(default="Review", init=False)
