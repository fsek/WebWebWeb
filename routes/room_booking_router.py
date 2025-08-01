from fastapi import APIRouter, HTTPException
from api_schemas.room_booking_schemas import (
    RoomBookingCreate,
    RoomBookingRead,
    RoomBookingUpdate,
    RoomBookingsBetweenDates,
)
from database import DB_dependency
from typing import Annotated
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.council_model import Council_DB
from db_models.room_booking_model import RoomBooking_DB
from helpers.types import ROOMS


room_router = APIRouter()


@room_router.post("/", response_model=RoomBookingRead, dependencies=[Permission.member()])
def create_room_booking(
    data: RoomBookingCreate,
    current_user: Annotated[User_DB, Permission.member()],
    db: DB_dependency,
    manage_permission: Annotated[bool, Permission.check("manage", "RoomBookings")],
):
    if data.end_time <= data.start_time:
        raise HTTPException(400, "End time must be after start time")
    if data.start_time == data.end_time:
        raise HTTPException(400, detail="Booking start time cannot be equal to end time.")

    overlapping_booking = (
        db.query(RoomBooking_DB)
        .filter(
            (RoomBooking_DB.room == data.room)
            & (RoomBooking_DB.start_time < data.end_time)
            & (data.start_time < RoomBooking_DB.end_time)
        )
        .first()  # one_or_none() raises an error if multiple bookings found, we just want to refuse the booking
    )

    if overlapping_booking:
        raise HTTPException(400, "The booking clashes with another booking")

    # Require council_id if not personal booking
    if not data.personal and data.council_id is None:
        raise HTTPException(400, detail="Council ID is required for non-personal bookings.")

    # Remove council_id if personal booking
    if data.personal and data.council_id is not None:
        data.council_id = None

    council = db.query(Council_DB).filter_by(id=data.council_id).one_or_none()
    if council is None and not data.personal:
        raise HTTPException(404, "Council not found")

    # Disallow regular users from booking cars for other councils
    if not manage_permission and data.council_id is not None:  # For safety, we don't care if it is a personal booking
        if data.council_id not in [post.council_id for post in current_user.posts]:
            raise HTTPException(403, detail="You do not have permission to book rooms for this council.")

    room_booking = RoomBooking_DB(
        room=data.room,
        start_time=data.start_time,
        end_time=data.end_time,
        description=data.description,
        council_id=data.council_id,
        user_id=current_user.id,
        personal=data.personal,
    )

    db.add(room_booking)
    db.commit()

    return room_booking


@room_router.get("/get_booking/{booking_id}", response_model=RoomBookingRead, dependencies=[Permission.member()])
def get_room_booking(booking_id: int, db: DB_dependency):
    booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, detail="Room booking not found")
    return booking


@room_router.get("/get_all", response_model=list[RoomBookingRead], dependencies=[Permission.member()])
def get_all_room_bookings(db: DB_dependency):
    bookings = db.query(RoomBooking_DB).all()
    return bookings


# Får göra en fuling här o göra routen till en post för att kunna skicka med en JSON body
@room_router.post("/get_between_times", response_model=list[RoomBookingRead], dependencies=[Permission.member()])
def get_room_bookings_between_times(db: DB_dependency, data: RoomBookingsBetweenDates):
    bookings = (
        db.query(RoomBooking_DB)
        .filter((RoomBooking_DB.start_time >= data.start_time) & (RoomBooking_DB.end_time <= data.end_time))
        .all()
    )
    return bookings


@room_router.get("/get_by_room/", response_model=list[RoomBookingRead], dependencies=[Permission.member()])
def get_bookings_by_room(room: ROOMS, db: DB_dependency):
    bookings = db.query(RoomBooking_DB).filter(RoomBooking_DB.room == room)
    return bookings


@room_router.delete("/{booking_id}", response_model=RoomBookingRead, dependencies=[Permission.member()])
def remove_room_booking(
    booking_id: int,
    db: DB_dependency,
    current_user: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "RoomBookings")],
):
    booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, "Room booking not found")

    if (booking.user == current_user) or manage_permission:
        db.delete(booking)
        db.commit()
        return booking
    raise HTTPException(401, detail="You do not have permission to delete this booking.")


@room_router.patch("/{booking_id}", response_model=RoomBookingRead, dependencies=[Permission.member()])
def update_room_booking(
    booking_id: int,
    data: RoomBookingUpdate,
    current_user: Annotated[User_DB, Permission.member()],
    db: DB_dependency,
    manage_permission: Annotated[bool, Permission.check("manage", "RoomBookings")],
):
    booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, "Room booking not found")
    if (booking.user != current_user) and (not manage_permission):
        raise HTTPException(401, detail="You do not have permission to update this booking.")

    for var, value in vars(data).items():
        setattr(booking, var, value) if value is not None else None

    if data.end_time is None:
        data.end_time = booking.end_time
    if data.start_time is None:
        data.start_time = booking.start_time

    if data.end_time <= data.start_time:
        raise HTTPException(400, "End time must be after start time")
    if data.start_time == data.end_time:
        raise HTTPException(400, detail="Booking start time cannot be equal to end time.")

    overlapping_booking = (
        db.query(RoomBooking_DB)
        .filter(
            (RoomBooking_DB.id != booking.id)
            & (RoomBooking_DB.room == booking.room)
            & (RoomBooking_DB.start_time < data.end_time)
            & (data.start_time < RoomBooking_DB.end_time)
        )
        .first()
    )

    if overlapping_booking:
        raise HTTPException(400, "The booking clashes with another booking")

    for var, value in vars(data).items():
        setattr(booking, var, value) if value else None

    db.commit()
    db.refresh(booking)
    return booking
