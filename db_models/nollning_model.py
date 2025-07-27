from db_models.base_model import BaseModel_DB

from sqlalchemy import String
from db_models.base_model import BaseModel_DB
from typing import TYPE_CHECKING

from helpers.constants import MAX_NOLLNING_DESC, MAX_NOLLNING_NAME
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db_models.nollning_group_model import NollningGroup_DB

from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

if TYPE_CHECKING:
    from db_models.adventure_mission_model import AdventureMission_DB
    from db_models.group_model import Group_DB


class Nollning_DB(BaseModel_DB):
    __tablename__ = "nollning_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column(String(MAX_NOLLNING_NAME))

    description: Mapped[str] = mapped_column(String(MAX_NOLLNING_DESC))

    year: Mapped[int] = mapped_column()

    missions: Mapped[list["AdventureMission_DB"]] = relationship(
        back_populates="nollning", cascade="all, delete-orphan", init=False
    )

    nollning_groups: Mapped[list["NollningGroup_DB"]] = relationship(
        back_populates="nollning", cascade="all, delete-orphan", init=False
    )

    groups: AssociationProxy[list["Group_DB"]] = association_proxy(
        target_collection="nollning_groups", attr="group", init=False
    )
