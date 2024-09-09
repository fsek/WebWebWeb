from fastapi import APIRouter, HTTPException,status
from api_schemas.car_booking_schema import CarCreate, CarRead
from database import DB_dependency
from typing import Annotated
from sqlalchemy import or_, and_


from user.permission import Permission
from db_models.user_model import User_DB
from db_models.car_model import Car_DB

car_router = APIRouter()

@car_router.get("/", response_model=list[CarRead], dependencies=[Permission.member()])
def get_all_booking(db: DB_dependency):
    bookings = db.query(Car_DB).all()
    return bookings

@car_router.post("/", response_model=CarCreate)
def create_booking(booking:CarCreate,current_user:Annotated[User_DB, Permission.member()],db: DB_dependency):
    if booking.end_time < booking.start_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    #illegal = db.query(Car_DB).filter((booking.start_time < Car_DB.start_time & booking.end_time > Car_DB.start_time) | (booking.start_time < Car_DB.end_time & booking.end_time > Car_DB.end_time) | (booking.start_time > Car_DB.start_time & booking.end_time < Car_DB.end_time))
    illegal_booking = db.query(Car_DB).filter(
        and_(
            Car_DB.user_id == current_user.id,  # Ensure user is booking their own cars
            or_(
                and_(booking.start_time >= Car_DB.start_time, booking.start_time < Car_DB.end_time),
                and_(booking.end_time > Car_DB.start_time, booking.end_time <= Car_DB.end_time),
                and_(booking.start_time <= Car_DB.start_time, booking.end_time >= Car_DB.end_time)
            )
        )
    ).first()
    if illegal_booking:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    db_booking = Car_DB(start_time = booking.start_time, end_time = booking.end_time, user = current_user, user_id = current_user.id, description = booking.description)
    db.add(db_booking)
    db.commit()
    return db_booking

@car_router.delete("/", response_model=CarRead)
def remove_booking(booking_id:int,current_user:Annotated[User_DB, Permission.member()],manage_permission:Annotated[bool, Permission.check_permission("manage","Car")], db: DB_dependency):
    car_booking = db.query(Car_DB).filter(Car_DB.booking_id==booking_id).first()
    if car_booking is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    if (car_booking.user == current_user) | manage_permission:
        db.delete(car_booking)
        db.commit()
        return car_booking
    
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    
    