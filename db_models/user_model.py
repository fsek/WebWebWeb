from typing import TYPE_CHECKING, Callable, List, Optional
from fastapi_users_pelicanq.db import SQLAlchemyBaseUserTable
from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship, mapped_column
from helpers.constants import MAX_FIRST_NAME_LEN, MAX_LAST_NAME_LEN, MAX_TELEPHONE_LEN
from helpers.types import MEMBER_TYPE, USER_FOOD_PREFERENCES
from .base_model import BaseModel_DB
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from .post_user_model import PostUser_DB
from sqlalchemy import Enum, ARRAY
import datetime
from helpers.types import datetime_utc, USER_FOOD_PREFERENCES
from .ad_model import BookAd_DB
from .car_model import CarBooking_DB


if TYPE_CHECKING:
    from .post_model import Post_DB
    from .event_user_model import EventUser_DB
    from .post_user_model import PostUser_DB
    from .event_model import Event_DB
    from .news_model import News_DB
    from .ad_model import BookAd_DB


# called by SQLAlchemy when user.posts.append(some_post)
post_user_creator: Callable[["Post_DB"], "PostUser_DB"] = lambda post: PostUser_DB(post=post)


class User_DB(BaseModel_DB, SQLAlchemyBaseUserTable[int]):
    __tablename__ = "user_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)  # type: ignore . It's fine

    first_name: Mapped[str] = mapped_column(String(MAX_FIRST_NAME_LEN))
    last_name: Mapped[str] = mapped_column(String(MAX_LAST_NAME_LEN))
    telephone_number: Mapped[str] = mapped_column(String(MAX_TELEPHONE_LEN))

    food_custom: Mapped[str] = mapped_column(String, nullable=True)
    
    food_preferences: Mapped[List[USER_FOOD_PREFERENCES]] = mapped_column(
    ARRAY(String), default=None, nullable=True
    )

    book_ads: Mapped[list["BookAd_DB"]] = relationship(back_populates="user", cascade="all, delete-orphan", init=False)

    start_year: Mapped[int] = mapped_column(default=datetime.date.today().year)  # start year at the guild


    account_created: Mapped[datetime_utc] = mapped_column(
        default=datetime.datetime.now()
    )  # date and time the account was created

    start_year: Mapped[int] = mapped_column(default=datetime.date.today().year)  # start year at the guild

    program: Mapped[Optional[str]] = mapped_column(
        Enum("F", "N", "Pi", name="program_enum"), default=None
    )  # program at the guild

    account_created: Mapped[datetime_utc] = mapped_column(
        default=datetime.datetime.now()
    )  # date and time the account was created

    car_bookings: Mapped[list["CarBooking_DB"]] = relationship(back_populates="user", init=False)

    post_users: Mapped[list["PostUser_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", init=False
    )

    event_users: Mapped[list["EventUser_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", init=False
    )
    news: Mapped[list["News_DB"]] = relationship(back_populates="author", init=False)

    member_type: Mapped[Optional[MEMBER_TYPE]] = mapped_column(String(200), default=None)

    posts: AssociationProxy[list["Post_DB"]] = association_proxy(
        target_collection="post_users", attr="post", init=False, creator=post_user_creator
    )

    events: AssociationProxy[list["Event_DB"]] = association_proxy(
        target_collection="event_users", attr="event", init=False
    )

    is_member: Mapped[bool] = mapped_column(default=False)

    want_notifications: Mapped[bool] = mapped_column(default=True)