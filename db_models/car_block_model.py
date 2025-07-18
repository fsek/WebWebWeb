from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db_models.base_model import BaseModel_DB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user_model import User_DB


class CarBlock_DB(BaseModel_DB):
    __tablename__ = "car_block_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_table.id"), nullable=False, index=True)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    blocked_by: Mapped[int] = mapped_column(Integer, ForeignKey("user_table.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)

    user: Mapped["User_DB"] = relationship("User_DB", foreign_keys=[user_id], init=False)
    blocked_by_user: Mapped["User_DB"] = relationship("User_DB", foreign_keys=[blocked_by], init=False)
