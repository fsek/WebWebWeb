from typing import TYPE_CHECKING, Optional

from helpers.constants import MAX_ALBUM_DESC, MAX_ALBUM_TITLE
from db_models.base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey

if TYPE_CHECKING:
    from .user_model import User_DB
    from .album_model import Album_DB


class Photographer_DB(BaseModel_DB):
    __tablename__ = "photographer_table"

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user_table.id"), primary_key=True)
    user: Mapped[Optional["User_DB"]] = relationship(back_populates="photographer", init=False)

    album_id: Mapped[Optional[int]] = mapped_column(ForeignKey("album_table.id"), primary_key=True)
    album: Mapped[Optional["Album_DB"]] = relationship(back_populates="photographer", init=False)
