from typing import TYPE_CHECKING, Optional
from sqlalchemy import Enum, ForeignKey

from .base_model import BaseModel_DB
from helpers.types import ALCOHOL_EVENT_TYPES, datetime_utc
from sqlalchemy.orm import relationship, Mapped, mapped_column
from helpers.db_util import created_at_column, latest_modified_column

if TYPE_CHECKING:
    from user_model import User_DB
    from event_model import Event_DB


class EventUser_DB(BaseModel_DB):
    __tablename__ = "event_user_table"

    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), primary_key=True)
    user: Mapped["User_DB"] = relationship(back_populates="event_users")

    event_id: Mapped[int] = mapped_column(ForeignKey("event_table.id"), primary_key=True)
    event: Mapped["Event_DB"] = relationship(back_populates="event_users")

    confirmed_status: Mapped[str] = mapped_column(
        Enum("confirmed", "unconfirmed", name="confirmed_enum"), default="unconfirmed"
    )

    group_name: Mapped[Optional[str]] = mapped_column(default=None)
    priority: Mapped[str] = mapped_column(default="Övrigt")
    drinkPackage: Mapped[ALCOHOL_EVENT_TYPES] = mapped_column(default="None")

    created_at: Mapped[datetime_utc] = created_at_column()
    latest_modified: Mapped[datetime_utc] = latest_modified_column()
