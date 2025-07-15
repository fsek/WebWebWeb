from typing import TYPE_CHECKING, Optional

from sqlalchemy import String

from db_models.room_booking_model import RoomBooking_DB
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from helpers.constants import MAX_COUNCIL_DESC

if TYPE_CHECKING:
    from .post_model import Post_DB
    from .event_model import Event_DB


class Council_DB(BaseModel_DB):
    __tablename__ = "council_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column(String(160), unique=True)

    posts: Mapped[list["Post_DB"]] = relationship(back_populates="council", init=False)

    events: Mapped[list["Event_DB"]] = relationship(back_populates="council", init=False)

    room_bookings: Mapped[list["RoomBooking_DB"]] = relationship(back_populates="council", init=False)

    description: Mapped[Optional[str]] = mapped_column(String(MAX_COUNCIL_DESC))

    pass
