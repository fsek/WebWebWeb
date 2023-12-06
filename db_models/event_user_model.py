from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from base_model import BaseModel_DB

from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from event_model import Event_DB
    from user_model import User_DB


class EventUser_DB(BaseModel_DB):
    __tablename__ = "event_users_table"

    id: Mapped[int] = mapped_column(primary_key=True)

    user: Mapped["User_DB"] = relationship()
    user_id: Mapped[int] = mapped_column(ForeignKey("users_table"))

    event: Mapped["Event_DB"] = relationship()
    event_id: Mapped[int] = mapped_column(ForeignKey("events_table"))
