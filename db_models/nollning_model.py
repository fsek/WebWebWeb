from db_models.adventure_mission_model import AdventureMission_DB
from db_models.base_model import BaseModel_DB

from datetime import datetime

from sqlalchemy import String
from db_models.base_model import BaseModel_DB
from typing import TYPE_CHECKING

from helpers.constants import MAX_NOLLNING_DESC, MAX_NOLLNING_NAME
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


class Nollning_DB(BaseModel_DB):
    __tablename__ = "nollning_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column(String(MAX_NOLLNING_NAME))

    description: Mapped[str] = mapped_column(String(MAX_NOLLNING_DESC))

    missions: Mapped[list["AdventureMission_DB"]] = relationship(back_populates="nollning", init=False)
