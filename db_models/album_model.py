from os import path
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column

if TYPE_CHECKING:
    from .img_model import Img_DB


class Album_DB(BaseModel_DB):
    __tablename__ = "album_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column()

    imgs: Mapped[list["Img_DB"]] = relationship(back_populates="album", init=False)
