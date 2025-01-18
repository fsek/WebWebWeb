from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey

from db_models.group_mission_model import GroupMission_DB

from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from user_model import User_DB
    from db_models.group_model import Group_DB
    from db_models.nollning_model import Nollning_DB


class NollningGroup_DB(BaseModel_DB):
    __tablename__ = "nollning_group_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    nollning: Mapped["Nollning_DB"] = relationship(back_populates="nollning_groups")
    nollning_id: Mapped[int] = mapped_column(ForeignKey("nollning_table.id"))

    group: Mapped["Group_DB"] = relationship(back_populates="nollning_groups")
    group_id: Mapped[int] = mapped_column(ForeignKey("group_table.id"))

    group_missions: Mapped[list["GroupMission_DB"]] = relationship(
        back_populates="nollning_group", cascade="all, delete-orphan", init=False
    )
