from typing import TYPE_CHECKING

from helpers.constants import MAX_TAG_NAME
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String

if TYPE_CHECKING:
    from db_models.event_tag_model import EventTag_DB
    from db_models.news_tag_model import NewsTag_DB


class Tag_DB(BaseModel_DB):
    __tablename__ = "tag_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column(String(MAX_TAG_NAME), unique=True)

    news_tags: Mapped[list["NewsTag_DB"]] = relationship(back_populates="tag", cascade="all, delete-orphan", init=False)

    event_tags: Mapped[list["EventTag_DB"]] = relationship(
        back_populates="tag", cascade="all, delete-orphan", init=False
    )
