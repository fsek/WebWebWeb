from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from .base_model import BaseModel_DB

from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from event_model import Event_DB
    from user_model import User_DB


class EventUser_DB(BaseModel_DB):
    __tablename__ = "event_user_table"

    user: Mapped["User_DB"] = relationship(back_populates="event_user")
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), primary_key=True)

    event: Mapped["Event_DB"] = relationship(back_populates="event_user")
    event_id: Mapped[int] = mapped_column(ForeignKey("event_table.id"), primary_key=True)
