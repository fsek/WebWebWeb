from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship, mapped_column
from .base_model import BaseModel_DB
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from sqlalchemy.orm import MappedAsDataclass

if TYPE_CHECKING:
    from .event_model import Event_DB
    from .event_user_model import EventUser_DB
    from .post_model import Post_DB
    from .post_user_model import PostUser_DB


# creator: Callable[[Post_DB], PostUser_DB] = lambda post: PostUser_DB(post=post)


class Mixin(MappedAsDataclass, SQLAlchemyBaseUserTable[int]):
    pass


class User_DB(BaseModel_DB, Mixin):
    __tablename__ = "user_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)  # type: ignore . It's fine

    # email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    # hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    # is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    firstname: Mapped[str] = mapped_column()

    post_users: Mapped[list["PostUser_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", init=False
    )

    event_users: Mapped[list["EventUser_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", init=False
    )

    posts: AssociationProxy[list["Post_DB"]] = association_proxy(
        target_collection="post_users", attr="post", init=False
    )

    events: AssociationProxy[list["Event_DB"]] = association_proxy(
        target_collection="event_users", attr="event", init=False
    )

    # notifications: Mapped[list["Notification_DB"]]

    # fredmansky: Mapped["Fredmansky_DB"]
