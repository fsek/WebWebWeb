from datetime import datetime
from helpers.constants import MAX_ROOM_DESC
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, String

if TYPE_CHECKING:
    from .user_model import User_DB
    from .council_model import Council_DB


class RoomBooking_DB(BaseModel_DB):
    __tablename__ = "room_booking_table"
    booking_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    room_id: Mapped[int] = mapped_column()
    room: Mapped[str] = mapped_column()

    start_time: Mapped[datetime] = mapped_column()
    end_time: Mapped[datetime] = mapped_column()

    description: Mapped[str] = mapped_column(String(MAX_ROOM_DESC))

    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    user: Mapped["User_DB"] = relationship("User_DB", back_populates="room_bookings", init=False)

    council_id: Mapped[int] = mapped_column(ForeignKey("council_table.id"))
    council: Mapped["Council_DB"] = relationship("Council_DB", back_populates="room_bookings", init=False)

    pass
