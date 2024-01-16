from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column

# from .post_user_model import PostUser_DB

if TYPE_CHECKING:
    from .post_model import Post_DB
    from .permission_model import Permission_DB


class PostPermission_DB(BaseModel_DB):
    __tablename__ = "post_permission_table"

    post_id: Mapped[int] = mapped_column(ForeignKey("post_table.id"), primary_key=True, init=False)
    post: Mapped["Post_DB"] = relationship(back_populates="post_permissions", default=None)

    permission: Mapped["Permission_DB"] = relationship(back_populates="post_permissions", default=None)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permission_table.id"), primary_key=True, init=False)
