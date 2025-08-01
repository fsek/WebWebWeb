from fastapi import APIRouter, HTTPException
from api_schemas.room_booking_schemas import (
    RoomBookingCreate,
    RoomBookingRead,
    RoomBookingUpdate,
    RoomBookingsBetweenDates,
)
from database import DB_dependency
import datetime
from typing import Annotated
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.room_booking_model import RoomBooking_DB
from helpers.types import ROOMS
from services.room_booking_service import create_new_room_booking

room_router = APIRouter()


@room_router.post(
    "/", response_model=list[RoomBookingRead], dependencies=[Permission.require("manage", "RoomBookings")]
)
def create_room_booking(
    data: RoomBookingCreate,
    current_user: Annotated[User_DB, Permission.require("manage", "RoomBookings")],
    db: DB_dependency,
):
    room_booking = create_new_room_booking(data, current_user, db)

    booking_list: list["RoomBooking_DB"] = [room_booking]

    if not (data.recur_interval_days is None or data.recur_until is None):
        if data.recur_interval_days < 1:
            raise HTTPException(400, "Invalid argument for recurring interval days")

        index = 0
        first_start = data.start_time

        delta = datetime.timedelta(days=data.recur_interval_days)
        current_start = data.start_time + delta

        while (
            current_start <= data.recur_until
            and current_start < first_start + datetime.timedelta(days=365 * 2)
            and index < 50
        ):
            booking_clone = data.model_copy(
                update={
                    "start_time": current_start,
                    "end_time": data.end_time + delta,
                }
            )
            booking = create_new_room_booking(booking_clone, current_user, db)
            booking_list.append(booking)

            delta += datetime.timedelta(days=data.recur_interval_days)
            current_start = data.start_time + delta
            index += 1

    db.add_all(booking_list)
    db.commit()

    return booking_list


@room_router.get(
    "/get_booking/{booking_id}",
    response_model=RoomBookingRead,
    dependencies=[Permission.member()],
)
def get_room_booking(booking_id: int, db: DB_dependency):
    booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, detail="Room booking not found")
    return booking


@room_router.get(
    "/get_all",
    response_model=list[RoomBookingRead],
    dependencies=[Permission.member()],
)
def get_all_room_bookings(db: DB_dependency):
    bookings = db.query(RoomBooking_DB).all()
    return bookings


# Får göra en fuling här o göra routen till en post för att kunna skicka med en JSON body
@room_router.post(
    "/get_between_times",
    response_model=list[RoomBookingRead],
    dependencies=[Permission.member()],
)
def get_room_bookings_between_times(db: DB_dependency, data: RoomBookingsBetweenDates):
    bookings = (
        db.query(RoomBooking_DB)
        .filter((RoomBooking_DB.start_time >= data.start_time) & (RoomBooking_DB.end_time <= data.end_time))
        .all()
    )
    return bookings


@room_router.get(
    "/get_by_room/",
    response_model=list[RoomBookingRead],
    dependencies=[Permission.member()],
)
def get_bookings_by_room(room: ROOMS, db: DB_dependency):
    bookings = db.query(RoomBooking_DB).filter(RoomBooking_DB.room == room)
    return bookings


@room_router.delete(
    "/{booking_id}", response_model=RoomBookingRead, dependencies=[Permission.require("manage", "RoomBookings")]
)
def remove_room_booking(
    booking_id: int,
    db: DB_dependency,
):
    booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, "Room booking not found")

    db.delete(booking)
    db.commit()
    return booking


@room_router.patch(
    "/{booking_id}", response_model=RoomBookingRead, dependencies=[Permission.require("manage", "RoomBookings")]
)
def update_room_booking(
    booking_id: int,
    data: RoomBookingUpdate,
    db: DB_dependency,
):
    booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, "Room booking not found")

    # Fill in missing values with current booking values
    new_start = data.start_time if data.start_time is not None else booking.start_time
    new_end = data.end_time if data.end_time is not None else booking.end_time

    if new_end <= new_start:
        raise HTTPException(400, "End time must be after start time")
    if new_start == new_end:
        raise HTTPException(400, detail="Booking start time cannot be equal to end time.")

    overlapping_booking = (
        db.query(RoomBooking_DB)
        .filter(
            (RoomBooking_DB.id != booking.id)
            & (RoomBooking_DB.room == booking.room)
            & (RoomBooking_DB.start_time < new_end)
            & (new_start < RoomBooking_DB.end_time)
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
