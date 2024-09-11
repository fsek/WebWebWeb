from datetime import datetime
from helpers.constants import MAX_CAR_DESC
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, String

if TYPE_CHECKING:
   from .user_model import User_DB
 

class CarBooking_DB(BaseModel_DB):
    __tablename__ = "car_booking_table"

    booking_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    
    start_time: Mapped[datetime] = mapped_column()
    
    end_time: Mapped[datetime] = mapped_column()

    description: Mapped[Optional[str]] = mapped_column(String(MAX_CAR_DESC))
    
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
        
    user: Mapped["User_DB"] = relationship("User_DB", back_populates="car_bookings",init = False)
    pass
