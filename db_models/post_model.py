from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from .base_model import BaseModel_DB
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from sqlalchemy.orm import relationship, Mapped, mapped_column

if TYPE_CHECKING:
    from council_model import Council_DB
    from post_user_model import PostUser_DB
    from user_model import User_DB


class Post_DB(BaseModel_DB):
    __tablename__ = "post_table"

    id: Mapped[int] = mapped_column(primary_key=True)

    council: Mapped["Council_DB"] = relationship()
    council_id: Mapped[int] = mapped_column(ForeignKey("council_table.id"))

    post_users: Mapped[list["PostUser_DB"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )

    users: AssociationProxy[list["User_DB"]] = association_proxy(
        target_collection="post_users", attr="user"
    )

    # has many users through postusers
