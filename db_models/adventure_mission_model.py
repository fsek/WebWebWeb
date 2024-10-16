from datetime import datetime

from sqlalchemy import String
from db_models.base_model import BaseModel_DB
from typing import TYPE_CHECKING

from helpers.constants import MAX_ADVENTURE_MISSION_DESC, MAX_ADVENTURE_MISSION_NAME
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


class AdventureMission_DB(BaseModel_DB):
    __tablename__ = "Adventure_mssion_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    nollning_week: Mapped[int] = mapped_column()

    title: Mapped[str] = mapped_column(String(MAX_ADVENTURE_MISSION_NAME))

    description: Mapped[str] = mapped_column(String(MAX_ADVENTURE_MISSION_DESC))

    points: Mapped[str] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
