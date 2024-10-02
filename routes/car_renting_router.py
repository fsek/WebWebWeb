from fastapi import APIRouter, HTTPException, status
from api_schemas.car_booking_schema import CarCreate, CarRead, CarUpdate
from database import DB_dependency
from typing import Annotated
from sqlalchemy import or_, and_
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.car_model import CarBooking_DB

car_router = APIRouter()


@car_router.get("/", response_model=list[CarRead], dependencies=[Permission.member()])
def get_all_booking(db: DB_dependency):
    bookings = db.query(CarBooking_DB).all()
    return bookings


@car_router.get(
    "/{booking_id}", response_model=CarRead, dependencies=[Permission.require("view", "Car"), Permission.member()]
)
def get_booking(booking_id: int, db: DB_dependency):
    booking = db.query(CarBooking_DB).filter(CarBooking_DB.booking_id == booking_id).first()
    if booking:
        return booking
    raise HTTPException(status.HTTP_404_NOT_FOUND)


@car_router.post("/", response_model=CarRead, dependencies=[Permission.require("manage", "Car")])
def create_booking(booking: CarCreate, current_user: Annotated[User_DB, Permission.member()], db: DB_dependency):
    if booking.end_time < booking.start_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    illegal_booking = (
        db.query(CarBooking_DB)
        .filter(
            or_(
                and_(booking.start_time >= CarBooking_DB.start_time, booking.start_time < CarBooking_DB.end_time),
                and_(booking.end_time > CarBooking_DB.start_time, booking.end_time <= CarBooking_DB.end_time),
                and_(booking.start_time <= CarBooking_DB.start_time, booking.end_time >= CarBooking_DB.end_time),
            )
        )
        .first()
    )
    if illegal_booking:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    db_booking = CarBooking_DB(
        start_time=booking.start_time,
        end_time=booking.end_time,
        user_id=current_user.id,
        description=booking.description,
    )
    db.add(db_booking)
    db.commit()
    return db_booking


@car_router.delete("/{booking_id}", response_model=CarRead)
def remove_booking(
    booking_id: int,
    current_user: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Car")],
    db: DB_dependency,
):
    car_booking = db.query(CarBooking_DB).filter(CarBooking_DB.booking_id == booking_id).first()
    if car_booking is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    if (car_booking.user == current_user) or manage_permission:
        db.delete(car_booking)
        db.commit()
        return car_booking

    raise HTTPException(status.HTTP_401_UNAUTHORIZED)


@car_router.patch("/{booking_id}", response_model=CarRead)
def update_booking(
    booking_id: int,
    data: CarUpdate,
    current_user: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Car")],
    db: DB_dependency,
):
    car_booking = db.query(CarBooking_DB).filter(CarBooking_DB.booking_id == booking_id).first()
    if car_booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if (car_booking.user != current_user) and (not manage_permission):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    illegal_booking = (
        db.query(CarBooking_DB)
        .filter(
            or_(
                and_(data.start_time >= CarBooking_DB.start_time, data.start_time < CarBooking_DB.end_time),
                and_(data.end_time > CarBooking_DB.start_time, data.end_time <= CarBooking_DB.end_time),
                and_(data.start_time <= CarBooking_DB.start_time, data.end_time >= CarBooking_DB.end_time),
            )  # This checks so that there is no overlap with other bookings before being added to the table
        )
        .first()
    )

    if illegal_booking:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    if data.description is not None:
        car_booking.description = data.description

    car_booking.start_time = data.start_time
    car_booking.end_time = data.end_time

    db.commit()
    return car_booking
