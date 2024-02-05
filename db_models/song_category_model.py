from sqlalchemy import String
from typing import TYPE_CHECKING
from helpers.constants import MAX_SONG_CATEGORY
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship

if TYPE_CHECKING:
    from db_models.song_model import Song_DB


class SongCategory_DB(BaseModel_DB):
    __tablename__ = "songcategory_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column(String(MAX_SONG_CATEGORY))

    songs: Mapped[list["Song_DB"]] = relationship(back_populates="category", init=False)

    pass
