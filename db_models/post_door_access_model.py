from typing import TYPE_CHECKING

from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey
from helpers.types import DOOR_ACCESSES

if TYPE_CHECKING:
    from .post_model import Post_DB


class PostDoorAccess_DB(BaseModel_DB):
    __tablename__ = "post_door_access_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    post: Mapped["Post_DB"] = relationship(back_populates="post_door_accesses", init=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post_table.id"))

    door: Mapped[DOOR_ACCESSES] = mapped_column()
