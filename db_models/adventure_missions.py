from db_models.base_model import BaseModel_DB
from typing import TYPE_CHECKING
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


class AdventureMission_DB(BaseModel_DB):
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
