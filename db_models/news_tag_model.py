from typing import TYPE_CHECKING
from db_models.base_model import BaseModel_DB
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from db_models.tag_model import Tag_DB

if TYPE_CHECKING:
    from db_models.news_model import News_DB


class NewsTag_DB(BaseModel_DB):
    __tablename__ = "news_tag_table"

    tag_id: Mapped[int] = mapped_column(ForeignKey("tag_table.id"), primary_key=True)
    tag: Mapped["Tag_DB"] = relationship(back_populates="news_tags")

    news_id: Mapped[int] = mapped_column(ForeignKey("news_table.id"), primary_key=True)
    news: Mapped["News_DB"] = relationship(back_populates="news_tags")
