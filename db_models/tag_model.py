from typing import TYPE_CHECKING, Optional
from db_models.event_tag_DB import EventTag_DB
from db_models.nollning_tag_model import NollningTag_DB
from helpers.constants import MAX_TAG_NAME
from helpers.types import TAG_TYPE
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, String


class Tag_DB(BaseModel_DB):
    __tablename__ = "tag_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    tag_type: Mapped[TAG_TYPE] = mapped_column(unique=True)

    nollning_tags: Mapped["NollningTag_DB"] = relationship(
        back_populates="tag", cascade="all, delete-orphan", init=False
    )

    event_tags: Mapped["EventTag_DB"] = relationship(back_populates="tag", cascade="all, delete-orphan", init=False)
