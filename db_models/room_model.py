from datetime import datetime

from db_models.council_model import Council_DB
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey

if TYPE_CHECKING:
    from .user_model import User_DB

    # vision - room with a id, description and booking


class Room_DB(BaseModel_DB):
    __tablename__ = "room_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    description: Mapped[str] = mapped_column()

    name: Mapped[Optional[str]] = mapped_column()

    # kan bara bokas av en person i taget. Kan vara fel key
    bookings: Mapped[list["RoomBooking_DB"]] = relationship("RoomBooking_DB", back_populates="room")

    ###Fortsätt lägga till
