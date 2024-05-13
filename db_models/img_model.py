from typing import Optional
from sqlalchemy import ForeignKey
from .album_model import Album_DB
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


class Img_DB(BaseModel_DB):
    __tablename__ = "img_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    path: Mapped[str] = mapped_column()

    album_id: Mapped[int] = mapped_column(ForeignKey("album_table.id"), default=None)

    album: Mapped["Album_DB"] = relationship(back_populates="imgs", init=False)
