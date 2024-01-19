from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from .base_model import BaseModel_DB
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

if TYPE_CHECKING:
    from .user_model import User_DB
    from event_user_model import EventUser_DB
    from .event_signup_model import EventSignup_DB
    from council_model import Council_DB


class Event_DB(BaseModel_DB):
    __tablename__ = "event_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    starts_at: Mapped[datetime] = mapped_column()
    ends_at: Mapped[datetime] = mapped_column()

    title_sv: Mapped[str] = mapped_column(String(100))
    title_en: Mapped[str] = mapped_column(String(100))

    description_sv: Mapped[str] = mapped_column(String(1000))
    description_en: Mapped[str] = mapped_column(String(1000))

    council_id: Mapped[int] = mapped_column(ForeignKey("council_table.id"))
    council: Mapped["Council_DB"] = relationship(back_populates="events", init=False)

    event_signups: Mapped[list["EventSignup_DB"]] = relationship(back_populates="event", init=False)

    event_users: Mapped[list["EventUser_DB"]] = relationship(
        back_populates="event", cascade="all, delete-orphan", init=False
    )

    users: AssociationProxy[list["User_DB"]] = association_proxy(
        target_collection="event_users", attr="user", init=False
    )
