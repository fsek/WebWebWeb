from typing import TYPE_CHECKING, Callable, Optional
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship, mapped_column
from helpers.constants import MAX_FIRSTNAME_LEN, MAX_LASTNAME_LEN, MAX_TELEPHONE_LEN
from helpers.types import MEMBER_TYPE
from .base_model import BaseModel_DB
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from .post_user_model import PostUser_DB

if TYPE_CHECKING:
    from .post_model import Post_DB
    from .event_user_model import EventUser_DB
    from .event_signup_model import EventSignup_DB
    from .post_user_model import PostUser_DB
    from .event_model import Event_DB
    from .news_model import News_DB

# called by SQLAlchemy when user.posts.append(some_post)
post_user_creator: Callable[["Post_DB"], "PostUser_DB"] = lambda post: PostUser_DB(post=post)


class User_DB(BaseModel_DB, SQLAlchemyBaseUserTable[int]):
    __tablename__ = "user_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)  # type: ignore . It's fine

    firstname: Mapped[str] = mapped_column(String(MAX_FIRSTNAME_LEN))
    lastname: Mapped[str] = mapped_column(String(MAX_LASTNAME_LEN))
    telephone_number: Mapped[str] = mapped_column(String(MAX_TELEPHONE_LEN))

    post_users: Mapped[list["PostUser_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", init=False
    )

    event_users: Mapped[list["EventUser_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", init=False
    )
    event_signups: Mapped[list["EventSignup_DB"]] = relationship(back_populates="user", init=False)

    news: Mapped[list["News_DB"]] = relationship(back_populates="author", init=False)

    member_type: Mapped[Optional[MEMBER_TYPE]] = mapped_column(String(200), default=None)

    posts: AssociationProxy[list["Post_DB"]] = association_proxy(
        target_collection="post_users", attr="post", init=False, creator=post_user_creator
    )

    events: AssociationProxy[list["Event_DB"]] = association_proxy(
        target_collection="event_users", attr="event", init=False
    )

    is_member: Mapped[bool] = mapped_column(default=False)

    # notifications: Mapped[list["Notification_DB"]]
    # fredmansky: Mapped["Fredmansky_DB"]
