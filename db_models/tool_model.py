from helpers.constants import MAX_TOOL_NAME, MAX_TOOL_DESC
from .base_model import BaseModel_DB
from .tool_booking_model import ToolBooking_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer

if TYPE_CHECKING:
    from .tool_booking_model import ToolBooking_DB


class Tool_DB(BaseModel_DB):
    __tablename__ = "tool_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name_sv: Mapped[str] = mapped_column(String(MAX_TOOL_NAME))
    name_en: Mapped[str] = mapped_column(String(MAX_TOOL_NAME))

    amount: Mapped[int] = mapped_column(Integer)

    bookings: Mapped[list["ToolBooking_DB"]] = relationship(
        back_populates="tool", cascade="all, delete-orphan", init=False
    )

    description_sv: Mapped[Optional[str]] = mapped_column(String(MAX_TOOL_DESC), default=None)
    description_en: Mapped[Optional[str]] = mapped_column(String(MAX_TOOL_DESC), default=None)

    pass
