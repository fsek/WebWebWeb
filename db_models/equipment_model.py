from helpers.constants import MAX_EQUIPMENT_NAME, MAX_EQUIPMENT_DESC
from .base_model import BaseModel_DB
from .equipment_booking_model import EquipmentBooking_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Integer

if TYPE_CHECKING:
    from .equipment_booking_model import EquipmentBooking_DB


class Equipment_DB(BaseModel_DB):
    __tablename__ = "equipment_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name_sv: Mapped[str] = mapped_column(String(MAX_EQUIPMENT_NAME))
    name_en: Mapped[str] = mapped_column(String(MAX_EQUIPMENT_NAME))

    amount: Mapped[int] = mapped_column(Integer)

    bookings: Mapped[list["EquipmentBooking_DB"]] = relationship(
        back_populates="equipment", cascade="all, delete-orphan", init=False
    )

    description_sv: Mapped[Optional[str]] = mapped_column(String(MAX_EQUIPMENT_DESC), default=None)
    description_en: Mapped[Optional[str]] = mapped_column(String(MAX_EQUIPMENT_DESC), default=None)
