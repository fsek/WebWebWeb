from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db_models.base_model import BaseModel_DB
from typing import TYPE_CHECKING

from helpers.constants import MAX_CAR_BLOCK
from helpers.db_util import created_at_column
from helpers.types import datetime_utc


if TYPE_CHECKING:
    from .user_model import User_DB


class CarBlock_DB(BaseModel_DB):
    __tablename__ = "car_block_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    reason: Mapped[str] = mapped_column(String(MAX_CAR_BLOCK), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), nullable=False, index=True)
    user: Mapped["User_DB"] = relationship(foreign_keys=[user_id], init=False)

    blocked_by: Mapped[int] = mapped_column(ForeignKey("user_table.id"), nullable=False)
    blocked_by_user: Mapped["User_DB"] = relationship(foreign_keys=[blocked_by], init=False)

    created_at: Mapped[datetime_utc] = created_at_column()
