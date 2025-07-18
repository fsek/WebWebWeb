from helpers.types import datetime_utc
from helpers.constants import MAX_CAR_DESC, MAX_FIRST_NAME_LEN, MAX_LAST_NAME_LEN
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, String

if TYPE_CHECKING:
    from .user_model import User_DB
    from council_model import Council_DB


class CarBooking_DB(BaseModel_DB):
    __tablename__ = "car_booking_table"

    booking_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    start_time: Mapped[datetime_utc] = mapped_column()

    end_time: Mapped[datetime_utc] = mapped_column()

    description: Mapped[Optional[str]] = mapped_column(String(MAX_CAR_DESC))

    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))

    user: Mapped["User_DB"] = relationship("User_DB", back_populates="car_bookings", init=False)

    user_first_name: Mapped[str] = mapped_column(String(MAX_FIRST_NAME_LEN))
    user_last_name: Mapped[str] = mapped_column(String(MAX_LAST_NAME_LEN))

    council_id: Mapped[Optional[int]] = mapped_column(ForeignKey("council_table.id"))
    council: Mapped[Optional["Council_DB"]] = relationship(back_populates="car_bookings", init=False)

    confirmed: Mapped[bool] = mapped_column(default=False)

    personal: Mapped[bool] = mapped_column(default=False)
