from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey

from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from user_model import User_DB
    from db_models.group_model import Group_DB
    from db_models.nollning_model import Nollning_DB


class NollningGroup_DB(BaseModel_DB):
    __tablename__ = "nollning_group_table"

    nollning: Mapped["Nollning_DB"] = relationship(back_populates="nollning_groups")
    nollning_id: Mapped[int] = mapped_column(ForeignKey("nollning_table.id"), primary_key=True)

    group: Mapped["Group_DB"] = relationship(back_populates="nollning_groups")
    group_id: Mapped[int] = mapped_column(ForeignKey("group_table.id"), primary_key=True)
