# DEPRECATED / UNUSED

from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column

if TYPE_CHECKING:
    from user_model import User_DB
    from cafe_shift_model import CafeShift_DB


class CafeWorker_DB(BaseModel_DB):
    __tablename__ = "cafe_worker_table"

    # id: Mapped[int] = mapped_column(primary_key=True, init=False)

    user: Mapped["User_DB"] = relationship(back_populates="cafe_users")
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), primary_key=True)

    cafe_shifts: Mapped[list["CafeShift_DB"]] = relationship(back_populates="cafe_worker")
