from helpers.types import datetime_utc
from typing import TYPE_CHECKING, Optional
from db_models.base_model import BaseModel_DB
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from helpers.constants import MAX_NEWS_CONTENT, MAX_NEWS_TITLE
from helpers.db_util import created_at_column

from db_models.news_tag_model import NewsTag_DB

if TYPE_CHECKING:
    from .user_model import User_DB


class News_DB(BaseModel_DB):
    __tablename__ = "news_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title_sv: Mapped[str] = mapped_column(String(MAX_NEWS_TITLE))

    title_en: Mapped[str] = mapped_column(String(MAX_NEWS_TITLE))

    content_sv: Mapped[str] = mapped_column(String(MAX_NEWS_CONTENT))

    content_en: Mapped[str] = mapped_column(String(MAX_NEWS_CONTENT))

    author_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))

    author: Mapped["User_DB"] = relationship(back_populates="news", init=False)

    created_at: Mapped[datetime_utc] = created_at_column()

    bumped_at: Mapped[datetime_utc] = created_at_column()

    pinned_from: Mapped[Optional[datetime_utc]] = mapped_column(default=None)

    pinned_to: Mapped[Optional[datetime_utc]] = mapped_column(default=None)

    news_tags: Mapped[list["NewsTag_DB"]] = relationship(
        back_populates="news", cascade="all, delete-orphan", init=False
    )

    # categories: Mapped[list["Category_DB"]]
    # image: Mapped["Image_DB"]
