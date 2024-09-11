from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from helpers.types import datetime_utc

if TYPE_CHECKING:
    from user_model import User_DB


class CafeShift_DB(BaseModel_DB):
    __tablename__ = "cafe_shift_table"

    shift_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    starts_at: Mapped[datetime_utc] = mapped_column()
    ends_at: Mapped[datetime_utc] = mapped_column()

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user_table.id"), default=None)
    user: Mapped[Optional["User_DB"]] = relationship(back_populates="cafe_shifts", init=False)
