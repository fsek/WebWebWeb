from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from db_models.base_model import BaseModel_DB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from helpers.db_util import created_at_column, latest_modified_column

if TYPE_CHECKING:
    from .user_model import User_DB
    from .event_model import Event_DB


class EventSignup_DB(BaseModel_DB):
    __tablename__ = "event_signup_table"

    event_id: Mapped[int] = mapped_column(ForeignKey("event_table.id"), primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), primary_key=True, init=False)

    user: Mapped["User_DB"] = relationship(back_populates="event_signups")
    event: Mapped["Event_DB"] = relationship(back_populates="event_signups")

    created_at: Mapped[datetime] = created_at_column()
    latest_modified: Mapped[datetime] = latest_modified_column()

    # going_as so user chooses post, member_type or special
