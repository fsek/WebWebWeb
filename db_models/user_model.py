from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, relationship, mapped_column
from .base_model import BaseModel_DB
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

if TYPE_CHECKING:
    from .event_model import Event_DB
    from .event_user_model import EventUser_DB
    from .post_model import Post_DB
    from .post_user_model import PostUser_DB


# creator: Callable[[Post_DB], PostUser_DB] = lambda post: PostUser_DB(post=post)


class User_DB(BaseModel_DB, SQLAlchemyBaseUserTable[int]):
    __tablename__ = "user_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)  # type: ignore . It's fine

    post_users: Mapped[list["PostUser_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    event_users: Mapped[list["EventUser_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    posts: AssociationProxy[list["Post_DB"]] = association_proxy(
        target_collection="post_users", attr="post"
    )

    events: AssociationProxy[list["Event_DB"]] = association_proxy(
        target_collection="event_users", attr="event"
    )

    # notifications: Mapped[list["Notification_DB"]]

    # fredmansky: Mapped["Fredmansky_DB"]
