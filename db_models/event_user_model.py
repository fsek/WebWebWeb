from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, DateTime, ForeignKey

# from helpers.types import MEMBER_TYPE
from .base_model import BaseModel_DB
from datetime import datetime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from helpers.db_util import created_at_column, latest_modified_column

if TYPE_CHECKING:
    from user_model import User_DB
    from event_model import Event_DB


class EventUser_DB(BaseModel_DB):
    __tablename__ = "event_user_table"

    user: Mapped["User_DB"] = relationship(back_populates="event_users")
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), primary_key=True)

    event: Mapped["Event_DB"] = relationship(back_populates="event_users")
    event_id: Mapped[int] = mapped_column(ForeignKey("event_table.id"), primary_key=True)

    group_name: Mapped[Optional[str]] = mapped_column(default=None)
    priority: Mapped[str] = mapped_column(default="Övrigt")

    created_at: Mapped[datetime] = created_at_column()
    latest_modified: Mapped[datetime] = latest_modified_column()
