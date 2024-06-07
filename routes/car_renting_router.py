from fastapi import APIRouter, HTTPException,status
from api_schemas.car_booking_schema import CarCreate, CarRead
from database import DB_dependency
from typing import TYPE_CHECKING, Annotated

from user.permission import Permission


if TYPE_CHECKING:
    from db_models.user_model import User_DB
    from db_models.car_model import Car_DB


car_router = APIRouter()

@car_router.get("/", response_model=list[CarRead])
def get_all_bookings(db: DB_dependency):
    bookings = db.query(Car_DB).all()
    return bookings

@car_router.post("/", response_model=CarCreate)
def create_booking(booking:CarCreate,current_user:Annotated[User_DB, Permission.base()],db: DB_dependency):
    if booking.end_time < booking.start_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    illegal = db.query(Car_DB).filter((booking.start_time < Car_DB.start_time & booking.end_time > Car_DB.start_time) | (booking.start_time < Car_DB.end_time & booking.end_time > Car_DB.end_time) | (booking.start_time > Car_DB.start_time & booking.end_time < Car_DB.end_time))
    if illegal:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    db_booking = Car_DB(start_time = booking.start_time, end_time = booking.end_time, user = current_user, user_id = current_user.id, description = booking.description)
    db.add(db_booking)
    return db_booking

