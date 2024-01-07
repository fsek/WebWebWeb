from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from .base_model import BaseModel_DB
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

if TYPE_CHECKING:
    from event_user_model import EventUser_DB
    from council_model import Council_DB
    from .user_model import User_DB


class Event_DB(BaseModel_DB):
    __tablename__ = "event_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    # event_signup: Mapped[EventSignu] = relationsip()

    starts_at: Mapped[DateTime] = mapped_column(nullable=False)

    ends_at: Mapped[DateTime] = mapped_column(nullable=False)

    description_sv: Mapped[str] = mapped_column()
    description_en: Mapped[str] = mapped_column()

    council_id: Mapped[int] = mapped_column(ForeignKey("council_table.id"))

    council: Mapped["Council_DB"] = relationship(back_populates="events")

    event_users: Mapped[list["EventUser_DB"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    users: AssociationProxy[list["User_DB"]] = association_proxy(target_collection="event_users", attr="user")

    # has many users through event users

    pass
