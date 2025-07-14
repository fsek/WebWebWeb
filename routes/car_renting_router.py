from fastapi import APIRouter, HTTPException, status
from api_schemas.car_booking_schema import CarCreate, CarRead, CarUpdate
from database import DB_dependency
from typing import Annotated
from services.car_renting_service import create_new_booking, booking_update, is_user_blocked
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.car_model import CarBooking_DB

car_router = APIRouter()


@car_router.get("/", response_model=list[CarRead], dependencies=[Permission.member()])
def get_all_booking(db: DB_dependency):
    bookings = db.query(CarBooking_DB).all()
    return bookings


@car_router.get("/{booking_id}", response_model=CarRead, dependencies=[Permission.member()])
def get_booking(booking_id: int, db: DB_dependency):
    booking = db.query(CarBooking_DB).filter(CarBooking_DB.booking_id == booking_id).first()
    if booking:
        return booking
    raise HTTPException(status.HTTP_404_NOT_FOUND)


@car_router.post("/", response_model=CarRead, dependencies=[Permission.member()])
def create_booking(
    booking: CarCreate,
    current_user: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Car")],
    db: DB_dependency,
):
    # Blocked users cannot book
    if is_user_blocked(current_user.id, db):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You are blocked from booking cars.")
    created_booking = create_new_booking(
        data=booking,
        db=db,
        current_user=current_user,
        manage_permission=manage_permission,
    )
    return created_booking


@car_router.delete("/{booking_id}", response_model=CarRead, dependencies=[Permission.member()])
def remove_booking(
    booking_id: int,
    current_user: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Car")],
    db: DB_dependency,
):
    # Blocked users cannot even delete bookings
    if is_user_blocked(current_user.id, db):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You are blocked from booking cars.")
    car_booking = db.query(CarBooking_DB).filter(CarBooking_DB.booking_id == booking_id).first()
    if car_booking is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    if (car_booking.user == current_user) or manage_permission:
        db.delete(car_booking)
        db.commit()
        return car_booking

    raise HTTPException(status.HTTP_401_UNAUTHORIZED)


@car_router.patch("/{booking_id}", response_model=CarRead, dependencies=[Permission.member()])
def update_booking(
    booking_id: int,
    data: CarUpdate,
    current_user: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Car")],
    db: DB_dependency,
):
    # Blocked users cannot edit bookings
    if is_user_blocked(current_user.id, db):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You are blocked from booking cars.")
    updated_booking = booking_update(
        booking_id=booking_id,
        data=data,
        current_user=current_user,
        manage_permission=manage_permission,
        db=db,
    )
    return updated_booking
