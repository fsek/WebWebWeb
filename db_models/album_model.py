from typing import TYPE_CHECKING
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from helpers.types import datetime_utc

if TYPE_CHECKING:
    from .img_model import Img_DB


# TODO idk, lots of shit


class Album_DB(BaseModel_DB):
    __tablename__ = "album_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    year: Mapped[int] = mapped_column()

    path: Mapped[str] = mapped_column()

    name: Mapped[str] = mapped_column()

    imgs: Mapped[list["Img_DB"]] = relationship(back_populates="album", init=False)
