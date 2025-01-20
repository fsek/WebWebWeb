from typing import TYPE_CHECKING, Optional
from helpers.constants import MAX_TAG_NAME
from helpers.types import TAG_TYPE
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, String

if TYPE_CHECKING:
    from db_models.nollning_model import Nollning_DB
    from db_models.tag_model import Tag_DB


class NollningTag_DB(BaseModel_DB):

    __tablename__ = "nollning_tag_table"

    name: Mapped[str] = mapped_column(String(MAX_TAG_NAME), unique=True)

    tag: Mapped["Tag_DB"] = relationship(back_populates="nollning_tags")
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag_table.id"), primary_key=True)

    nollning: Mapped["Nollning_DB"] = relationship(back_populates="nollning_tags")
    nollning_id: Mapped[int] = mapped_column(ForeignKey("nollning_table.id"), primary_key=True)
