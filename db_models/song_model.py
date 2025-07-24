from typing import TYPE_CHECKING

from db_models.song_category_model import SongCategory_DB
from helpers.constants import MAX_SONG_AUTHOR, MAX_SONG_CONTENT, MAX_SONG_TITLE, MAX_SONG_MELODY
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional
from sqlalchemy import ForeignKey, String


if TYPE_CHECKING:
    from .song_category_model import SongCategory_DB


class Song_DB(BaseModel_DB):
    __tablename__ = "song_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title: Mapped[str] = mapped_column(String(MAX_SONG_TITLE))

    content: Mapped[str] = mapped_column(String(MAX_SONG_CONTENT))

    author: Mapped[Optional[str]] = mapped_column(String(MAX_SONG_AUTHOR), default=None)

    melody: Mapped[Optional[str]] = mapped_column(String(MAX_SONG_MELODY), default=None)

    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("song_category_table.id"), default=None)

    category: Mapped[Optional["SongCategory_DB"]] = relationship(back_populates="songs", init=False)

    views: Mapped[int] = mapped_column(default=0)

    pass
