from helpers.types import datetime_utc
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from helpers.constants import MAX_EVENT_DESC, MAX_EVENT_LOCATION, MAX_EVENT_TITLE
from .base_model import BaseModel_DB
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from db_models.event_tag_model import EventTag_DB

if TYPE_CHECKING:
    from .user_model import User_DB
    from event_user_model import EventUser_DB
    from council_model import Council_DB
    from priority_model import Priority_DB


class Event_DB(BaseModel_DB):
    __tablename__ = "event_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    starts_at: Mapped[datetime_utc] = mapped_column()
    ends_at: Mapped[datetime_utc] = mapped_column()

    signup_start: Mapped[datetime_utc] = mapped_column()
    signup_end: Mapped[datetime_utc] = mapped_column()

    title_sv: Mapped[str] = mapped_column(String(MAX_EVENT_TITLE))
    title_en: Mapped[str] = mapped_column(String(MAX_EVENT_TITLE))

    description_sv: Mapped[str] = mapped_column(String(MAX_EVENT_DESC))
    description_en: Mapped[str] = mapped_column(String(MAX_EVENT_DESC))

    council_id: Mapped[int] = mapped_column(ForeignKey("council_table.id"))
    council: Mapped["Council_DB"] = relationship(back_populates="events", init=False)

    location: Mapped[str] = mapped_column(String(MAX_EVENT_LOCATION))

    max_event_users: Mapped[int] = mapped_column(default=0)

    event_users: Mapped[list["EventUser_DB"]] = relationship(
        back_populates="event", cascade="all, delete-orphan", init=False
    )

    users: AssociationProxy[list["User_DB"]] = association_proxy(
        target_collection="event_users", attr="user", init=False
    )

    priorities: Mapped[list["Priority_DB"]] = relationship(
        back_populates="event", cascade="all, delete-orphan", init=False
    )

    all_day: Mapped[bool] = mapped_column(default=False)
    signup_not_opened_yet: Mapped[bool] = mapped_column(default=True)
    recurring: Mapped[bool] = mapped_column(default=False)
    drink: Mapped[bool] = mapped_column(default=False)
    food: Mapped[bool] = mapped_column(default=False)
    cash: Mapped[bool] = mapped_column(default=False)
    closed: Mapped[bool] = mapped_column(default=False)
    can_signup: Mapped[bool] = mapped_column(default=False)
    drink_package: Mapped[bool] = mapped_column(default=False)

    event_tags: Mapped[list["EventTag_DB"]] = relationship(
        back_populates="event", cascade="all, delete-orphan", init=False
    )

    is_nollning_event: Mapped[bool] = mapped_column(default=False)
