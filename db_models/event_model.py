from typing import TYPE_CHECKING

from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base_model import BaseModel_DB


if TYPE_CHECKING:
    from event_user_model import EventUser_DB
    from council_model import Council_DB


class Event_DB(BaseModel_DB):
    __tablename__ = "event_table"

    id: Mapped[int] = mapped_column(primary_key=True)

    # event_signup: Mapped[EventSignu] = relationship()

    event_user: Mapped["EventUser_DB"] = relationship()
    council: Mapped["Council_DB"] = relationship()

    # has many users through event users

    pass
