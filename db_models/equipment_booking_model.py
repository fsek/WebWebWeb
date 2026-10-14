from helpers.constants import MAX_EQUIPMENT_BOOKING_DESC
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String
from helpers.types import datetime_utc

if TYPE_CHECKING:
    from .user_model import User_DB
    from .equipment_model import Equipment_DB


class EquipmentBooking_DB(BaseModel_DB):
    __tablename__ = "equipment_booking_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    amount: Mapped[int] = mapped_column()

    start_time: Mapped[datetime_utc] = mapped_column()
    end_time: Mapped[datetime_utc] = mapped_column()

    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment_table.id"))
    equipment: Mapped["Equipment_DB"] = relationship(back_populates="bookings", init=False)

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user_table.id", ondelete="CASCADE"))
    user: Mapped[Optional["User_DB"]] = relationship(back_populates="equipment_bookings", init=False)

    description: Mapped[Optional[str]] = mapped_column(String(MAX_EQUIPMENT_BOOKING_DESC), default=None)
