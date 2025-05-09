from typing import TYPE_CHECKING, Optional

from helpers.constants import MAX_ALBUM_DESC, MAX_ALBUM_TITLE
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from helpers.types import datetime_utc
from sqlalchemy import ForeignKey, String

if TYPE_CHECKING:
    from .img_model import Img_DB
    from .user_model import User_DB


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

    photographer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user_table.id"), default=None)

    photographer: Mapped["User_DB"] = relationship(back_populates="photographed_albums", init=False)

    imgs: Mapped[list["Img_DB"]] = relationship(back_populates="album", init=False)
