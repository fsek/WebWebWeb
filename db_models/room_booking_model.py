from helpers.constants import MAX_ROOM_DESC
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String
from helpers.types import ROOMS, datetime_utc

if TYPE_CHECKING:
    from .user_model import User_DB
    from .council_model import Council_DB


class RoomBooking_DB(BaseModel_DB):
    __tablename__ = "room_booking_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    room: Mapped[ROOMS] = mapped_column()

    start_time: Mapped[datetime_utc] = mapped_column()
    end_time: Mapped[datetime_utc] = mapped_column()

    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    user: Mapped["User_DB"] = relationship(back_populates="room_bookings", init=False)

    council_id: Mapped[int] = mapped_column(ForeignKey("council_table.id"))
    council: Mapped["Council_DB"] = relationship(back_populates="room_bookings", init=False)

    description: Mapped[Optional[str]] = mapped_column(String(MAX_ROOM_DESC), default=None)

    pass
