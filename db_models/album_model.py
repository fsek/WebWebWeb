from typing import TYPE_CHECKING, Optional

from helpers.constants import MAX_ALBUM_DESC, MAX_ALBUM_TITLE
from db_models.photographer_model import Photographer_DB
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from helpers.types import datetime_utc
from sqlalchemy import String

if TYPE_CHECKING:
    from .img_model import Img_DB


# TODO idk, lots of shit


class Album_DB(BaseModel_DB):
    __tablename__ = "album_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    year: Mapped[int] = mapped_column()

    path: Mapped[str] = mapped_column()

    location: Mapped[str] = mapped_column()

    date: Mapped[datetime_utc] = mapped_column()

    title_sv: Mapped[str] = mapped_column(String(MAX_ALBUM_TITLE))

    title_en: Mapped[str] = mapped_column(String(MAX_ALBUM_TITLE))

    desc_sv: Mapped[str] = mapped_column(String(MAX_ALBUM_DESC))

    desc_en: Mapped[str] = mapped_column(String(MAX_ALBUM_DESC))

    photographer: Mapped[list[Photographer_DB]] = relationship(
        back_populates="album", cascade="all, delete-orphan", init=False
    )

    imgs: Mapped[list["Img_DB"]] = relationship(back_populates="album", init=False)
