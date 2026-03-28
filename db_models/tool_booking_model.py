from helpers.constants import MAX_TOOL_BOOKING_DESC
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String
from helpers.types import datetime_utc

if TYPE_CHECKING:
    from .user_model import User_DB
    from .tool_model import Tool_DB


class ToolBooking_DB(BaseModel_DB):
    __tablename__ = "tool_booking_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    amount: Mapped[int] = mapped_column()

    start_time: Mapped[datetime_utc] = mapped_column()
    end_time: Mapped[datetime_utc] = mapped_column()

    tool_id: Mapped[int] = mapped_column(ForeignKey("tool_table.id"))
    tool: Mapped["Tool_DB"] = relationship(back_populates="bookings", init=False)

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user_table.id"))
    user: Mapped[Optional["User_DB"]] = relationship(back_populates="tool_bookings", init=False)

    description: Mapped[Optional[str]] = mapped_column(String(MAX_TOOL_BOOKING_DESC), default=None)

    pass
