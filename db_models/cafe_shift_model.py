from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from cafe_worker_model import CafeWorker_DB
    from event_model import Event_DB


class CafeShift_DB(BaseModel_DB):
    __tablename__ = "cafe_shift_table"

    starts_at: Mapped[datetime] = mapped_column()
    ends_at: Mapped[datetime] = mapped_column()

    cafe_worker: Mapped["CafeWorker_DB"] = relationship(back_populates="cafe_shift_users")
    cafe_worker_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), primary_key=True)
