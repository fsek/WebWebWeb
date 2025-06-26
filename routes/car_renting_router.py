from fastapi import APIRouter, HTTPException, status
from api_schemas.car_booking_schema import CarCreate, CarRead, CarUpdate
from database import DB_dependency
from typing import Annotated
from sqlalchemy import or_, and_, literal
import database
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.car_model import CarBooking_DB
from datetime import UTC, datetime

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
    booking_confirmed = True  # Default to confirmed unless conditions below change it
    if booking.end_time < booking.start_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    if booking.start_time == booking.end_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Booking start time cannot be equal to end time.")
    booking_overlaps_confirmed = (
        db.query(CarBooking_DB)
        .filter(
            and_(
                or_(
                    and_(booking.start_time >= CarBooking_DB.start_time, booking.start_time < CarBooking_DB.end_time),
                    and_(booking.end_time > CarBooking_DB.start_time, booking.end_time <= CarBooking_DB.end_time),
                    and_(booking.start_time <= CarBooking_DB.start_time, booking.end_time >= CarBooking_DB.end_time),
                ),
                CarBooking_DB.confirmed.is_(True),  # Only check confirmed bookings
            )
        )
        .first()
    )
    booking_overlaps_unconfirmed = (
        db.query(CarBooking_DB)
        .filter(
            and_(
                or_(
                    and_(booking.start_time >= CarBooking_DB.start_time, booking.start_time < CarBooking_DB.end_time),
                    and_(booking.end_time > CarBooking_DB.start_time, booking.end_time <= CarBooking_DB.end_time),
                    and_(booking.start_time <= CarBooking_DB.start_time, booking.end_time >= CarBooking_DB.end_time),
                ),
                CarBooking_DB.confirmed.is_(False),  # Only check unconfirmed bookings
            )
        )
        .first()
    )
    if booking_overlaps_confirmed:
        booking_confirmed = False
    if booking_overlaps_unconfirmed and not manage_permission:
        booking_confirmed = False
    if booking.start_time < datetime.now(UTC):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Booking start time cannot be in the past.")

    if not manage_permission:
        # Unconfirm booking between 17:00 and 08:00
        if booking.start_time.hour < 8 or booking.start_time.hour >= 17:
            booking_confirmed = False
        if booking.end_time.hour < 8 or booking.end_time.hour >= 17:
            booking_confirmed = False
        # Unconfirm booking on weekends
        if booking.start_time.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            booking_confirmed = False

    db_booking = CarBooking_DB(
        start_time=booking.start_time,
        end_time=booking.end_time,
        user_id=current_user.id,
        description=booking.description,
        confirmed=booking_confirmed,
        personal=booking.personal,
        council_id=booking.council_id,
    )
    db.add(db_booking)
    db.commit()
    return db_booking


@car_router.delete("/{booking_id}", response_model=CarRead, dependencies=[Permission.member()])
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


@car_router.patch("/{booking_id}", response_model=CarRead, dependencies=[Permission.member()])
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

    if data.confirmed is not None:
        booking_confirmed = data.confirmed  # default to updated value, fallback to previous value
    else:
        booking_confirmed = car_booking.confirmed

    # only check for illegal overlap if new times are provided
    if data.start_time is not None or data.end_time is not None:
        # Use new values if provided, otherwise use existing values
        check_start_time = data.start_time if data.start_time is not None else car_booking.start_time
        check_end_time = data.end_time if data.end_time is not None else car_booking.end_time

        if check_start_time >= check_end_time:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail="Booking start time cannot be after nor equal to end time."
            )

        booking_overlaps_confirmed = (
            db.query(CarBooking_DB)
            .filter(
                and_(
                    or_(
                        and_(check_start_time >= CarBooking_DB.start_time, check_start_time < CarBooking_DB.end_time),
                        and_(check_end_time > CarBooking_DB.start_time, check_end_time <= CarBooking_DB.end_time),
                        and_(check_start_time <= CarBooking_DB.start_time, check_end_time >= CarBooking_DB.end_time),
                    ),  # This checks so that there is no overlap with other bookings before being added to the table
                    # filters out the booking we are editing
                    literal(booking_id) != CarBooking_DB.booking_id,
                    CarBooking_DB.confirmed.is_(True),  # Only check confirmed bookings
                )
            )
            .first()
        )
        booking_overlaps_unconfirmed = (
            db.query(CarBooking_DB)
            .filter(
                and_(
                    or_(
                        and_(check_start_time >= CarBooking_DB.start_time, check_start_time < CarBooking_DB.end_time),
                        and_(check_end_time > CarBooking_DB.start_time, check_end_time <= CarBooking_DB.end_time),
                        and_(check_start_time <= CarBooking_DB.start_time, check_end_time >= CarBooking_DB.end_time),
                    ),
                    literal(booking_id) != CarBooking_DB.booking_id,
                    CarBooking_DB.confirmed.is_(False),  # Only check unconfirmed bookings
                )
            )
            .first()
        )

        # Admin is trying to edit a confirmed booking that overlaps with a confirmed booking
        if manage_permission and booking_overlaps_confirmed and booking_confirmed:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Booking overlaps with another confirmed booking.")
        # User is trying to edit a confirmed booking that overlaps with a confirmed or unconfirmed booking
        if not manage_permission and (booking_overlaps_confirmed or booking_overlaps_unconfirmed):
            booking_confirmed = False

    if not manage_permission:
        # Unconfirm booking between 17:00 and 08:00
        if data.start_time is not None:
            if data.start_time.hour < 8 or data.start_time.hour >= 17:
                booking_confirmed = False
            # Unconfirm booking on weekends
            if data.start_time.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                booking_confirmed = False
        if data.end_time is not None:
            if data.end_time.hour < 8 or data.end_time.hour >= 17:
                booking_confirmed = False
            if data.end_time.weekday() >= 5:
                booking_confirmed = False

    car_booking.confirmed = booking_confirmed

    if data.description is not None:
        car_booking.description = data.description
    if data.start_time is not None:
        car_booking.start_time = data.start_time
    if data.end_time is not None:
        car_booking.end_time = data.end_time
    if data.personal is not None:
        car_booking.personal = data.personal
    if data.council_id is not None:
        car_booking.council_id = data.council_id

    db.commit()
    return car_booking
