from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from helpers.constants import MAX_EVENT_DESC, MAX_EVENT_TITLE
from .base_model import BaseModel_DB
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from priority_model import Priority_DB

if TYPE_CHECKING:
    from .user_model import User_DB
    from event_user_model import EventUser_DB
    from council_model import Council_DB


class Event_DB(BaseModel_DB):
    __tablename__ = "event_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    starts_at: Mapped[datetime] = mapped_column()
    ends_at: Mapped[datetime] = mapped_column()

    signup_start: Mapped[datetime] = mapped_column()
    signup_end: Mapped[datetime] = mapped_column()

    title_sv: Mapped[str] = mapped_column(String(MAX_EVENT_TITLE))
    title_en: Mapped[str] = mapped_column(String(MAX_EVENT_TITLE))

    description_sv: Mapped[str] = mapped_column(String(MAX_EVENT_DESC))
    description_en: Mapped[str] = mapped_column(String(MAX_EVENT_DESC))

    council_id: Mapped[int] = mapped_column(ForeignKey("council_table.id"))
    council: Mapped["Council_DB"] = relationship(back_populates="events", init=False)
    
    max_event_users: Mapped[int] = mapped_column(default=0)

    event_users: Mapped[list["EventUser_DB"]] = relationship(
        back_populates="event", cascade="all, delete-orphan", init=False
    )

    users: AssociationProxy[list["User_DB"]] = association_proxy(
        target_collection="event_users", attr="user", init=False
    )
    
    priorities: Mapped[list["Priority_DB"]] = relationship(
        back_populates="event", init=False
    )
