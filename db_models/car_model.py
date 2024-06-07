from datetime import datetime
from db_models.user_model import User_DB
from helpers.constants import MAX_CAR_DESC
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional
from sqlalchemy import ForeignKey, String



class Car_DB(BaseModel_DB):
    __tablename__ = "booking_table"

    booking_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    
    user: Mapped["User_DB"] = relationship(back_populates="event_users")
    
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    
    start_time: Mapped[datetime] = mapped_column()
    
    end_time: Mapped[datetime] = mapped_column()

    description: Mapped[Optional[str]] = mapped_column(String(MAX_CAR_DESC))

    pass
