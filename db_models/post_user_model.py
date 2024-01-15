from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from .base_model import BaseModel_DB

from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from post_model import Post_DB
    from user_model import User_DB


class PostUser_DB(BaseModel_DB):
    __tablename__ = "post_user_table"

    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), primary_key=True, init=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("post_table.id"), primary_key=True, init=False)

    post: Mapped["Post_DB"] = relationship(back_populates="post_users", default=None)
    user: Mapped["User_DB"] = relationship(back_populates="post_users", default=None)
