from typing import TYPE_CHECKING
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey
from helpers.types import datetime_utc, DOOR_ACCESSES

if TYPE_CHECKING:
    from .user_model import User_DB


class UserDoorAccess_DB(BaseModel_DB):
    __tablename__ = "user_door_access_table"

    user_access_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    user: Mapped["User_DB"] = relationship(back_populates="accesses", init=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))

    door: Mapped[DOOR_ACCESSES] = mapped_column()

    starttime: Mapped[datetime_utc] = mapped_column()
    endtime: Mapped[datetime_utc] = mapped_column()
