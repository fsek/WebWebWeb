from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from user_model import User_DB
    from event_model import Event_DB


class CafeWorker_DB(BaseModel_DB):
    __tablename__ = "cafe_worker_table"

    user: Mapped["User_DB"] = relationship(back_populates="cafe_worker_users")
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), primary_key=True)

    cafe_shift: Mapped["Event_DB"] = relationship(back_populates="cafe_worker_users")
    cafe_shift_id: Mapped[int] = mapped_column(ForeignKey("cafe_shift_table.id"), primary_key=True)
