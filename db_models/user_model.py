from typing import TYPE_CHECKING, Callable, Optional
from fastapi_users_pelicanq.db import SQLAlchemyBaseUserTable
from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, relationship, mapped_column
from db_models.album_model import Album_DB
from db_models.candidate_model import Candidate_DB
from db_models.group_model import Group_DB
from db_models.group_user_model import GroupUser_DB
from db_models.document_model import Document_DB
from db_models.room_booking_model import RoomBooking_DB
from helpers.db_util import created_at_column
from .user_door_access_model import UserDoorAccess_DB
from helpers.constants import MAX_FIRST_NAME_LEN, MAX_LAST_NAME_LEN, MAX_TELEPHONE_LEN
from helpers.types import MEMBER_TYPE
from .base_model import BaseModel_DB
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from .post_user_model import PostUser_DB
from sqlalchemy import Enum
import datetime
from helpers.types import datetime_utc
from .ad_model import BookAd_DB
from .car_booking_model import CarBooking_DB
from helpers.types import datetime_utc

if TYPE_CHECKING:
    from .post_model import Post_DB
    from .event_user_model import EventUser_DB
    from .post_user_model import PostUser_DB
    from .event_model import Event_DB
    from .news_model import News_DB
    from .ad_model import BookAd_DB
    from .cafe_shift_model import CafeShift_DB


# called by SQLAlchemy when user.posts.append(some_post)
post_user_creator: Callable[["Post_DB"], "PostUser_DB"] = lambda post: PostUser_DB(post=post)


class User_DB(BaseModel_DB, SQLAlchemyBaseUserTable[int]):
    __tablename__ = "user_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)  # type: ignore . It's fine

    first_name: Mapped[str] = mapped_column(String(MAX_FIRST_NAME_LEN))
    last_name: Mapped[str] = mapped_column(String(MAX_LAST_NAME_LEN))
    telephone_number: Mapped[str] = mapped_column(String(MAX_TELEPHONE_LEN))
    stil_id: Mapped[Optional[str]] = mapped_column(default=None)

    is_member: Mapped[bool] = mapped_column(default=False)

    start_year: Mapped[int] = mapped_column(default=datetime.date.today().year)  # start year at the guild

    account_created: Mapped[datetime_utc] = created_at_column()

    program: Mapped[Optional[str]] = mapped_column(
        Enum("F", "N", "Pi", name="program_enum"), default=None
    )  # program at the guild

    standard_food_preferences: Mapped[list[str]] = mapped_column(JSON, init=False, default=list)

    other_food_preferences: Mapped[Optional[str]] = mapped_column(init=False, default="")

    want_notifications: Mapped[bool] = mapped_column(default=True)

    car_bookings: Mapped[list["CarBooking_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", init=False
    )

    room_bookings: Mapped[list["RoomBooking_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", init=False
    )

    post_users: Mapped[list["PostUser_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", init=False
    )

    event_users: Mapped[list["EventUser_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", init=False
    )
    news: Mapped[list["News_DB"]] = relationship(back_populates="author", cascade="all, delete-orphan", init=False)

    book_ads: Mapped[list["BookAd_DB"]] = relationship(back_populates="user", cascade="all, delete-orphan", init=False)

    candidates: Mapped[list["Candidate_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", init=False
    )

    group_users: Mapped[list["GroupUser_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", init=False
    )

    cafe_shifts: Mapped[list["CafeShift_DB"]] = relationship(back_populates="user", init=False)

    accesses: Mapped[list["UserDoorAccess_DB"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", init=False
    )

    photographed_albums: Mapped[list[Album_DB]] = relationship(back_populates="photographer", init=False)

    uploaded_documents: Mapped[list[Document_DB]] = relationship(back_populates="author", init=False)

    groups: AssociationProxy[list["Group_DB"]] = association_proxy(
        target_collection="group_users", attr="group", init=False
    )

    posts: AssociationProxy[list["Post_DB"]] = association_proxy(
        target_collection="post_users", attr="post", init=False, creator=post_user_creator
    )

    events: AssociationProxy[list["Event_DB"]] = association_proxy(
        target_collection="event_users", attr="event", init=False
    )
