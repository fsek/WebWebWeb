from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey
from .album_model import Album_DB
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

if TYPE_CHECKING:
    from tag_model import Tag_DB


class Img_DB(BaseModel_DB):
    __tablename__ = "img_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    path: Mapped[str] = mapped_column()

    album_id: Mapped[int] = mapped_column(ForeignKey("album_table.id"), default=None)

    album: Mapped["Album_DB"] = relationship(back_populates="imgs", init=False)

    tags: AssociationProxy[list["Tag_DB"]] = association_proxy(target_collection="image_tags", attr="tag", init=False)
