from fastapi import APIRouter, HTTPException
from api_schemas.room_booking_schemas import (
    RoomBookingCreate,
    RoomBookingRead,
    RoomBookingUpdate,
    RoomBookingsBetweenDates,
)
from database import DB_dependency
from typing import Annotated
from sqlalchemy import or_, and_, literal
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.council_model import Council_DB
from db_models.room_booking_model import RoomBooking_DB
from helpers.types import datetime_utc, ROOMS


room_router = APIRouter()


@room_router.post("/", response_model=RoomBookingRead, dependencies=[Permission.require("manage", "Room Bookings")])
def create_booking(data: RoomBookingCreate, current_user: Annotated[User_DB, Permission.member()], db: DB_dependency):
    if data.end_time <= data.start_time:
        raise HTTPException(400, "End time must be after start time")

    overlapping_booking = (
        db.query(RoomBooking_DB)
        .filter(
            (RoomBooking_DB.room == data.room)
            & (RoomBooking_DB.start_time < data.end_time)
            & (data.start_time < RoomBooking_DB.end_time)
        )
        .one_or_none()
    )

    if overlapping_booking:
        raise HTTPException(400, "The booking clashes with another booking")

    council = db.query(Council_DB).filter_by(id=data.council_id).one_or_none()
    if council is None:
        raise HTTPException(404, "Council not found")

    room_booking = RoomBooking_DB(
        room=data.room,
        start_time=data.start_time,
        end_time=data.end_time,
        description=data.description,
        council_id=data.council_id,
        user_id=current_user.id,
    )

    db.add(room_booking)
    db.commit()

    return room_booking


@room_router.get(
    "/get_booking/{booking_id}",
    response_model=RoomBookingRead,
    dependencies=[Permission.require("view", "Room Bookings")],
)
def get_booking(booking_id: int, db: DB_dependency):
    booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, detail="Room booking not found")
    return booking


@room_router.get(
    "/get_all", response_model=list[RoomBookingRead], dependencies=[Permission.require("view", "Room Bookings")]
)
def get_all_bookings(db: DB_dependency):
    bookings = db.query(RoomBooking_DB).all()
    return bookings


# Får göra en fuling här o göra routen till en post för att kunna skicka med en JSON body
@room_router.post(
    "/get_between_times",
    response_model=list[RoomBookingRead],
    dependencies=[Permission.require("view", "Room Bookings")],
)
def get_bookings_between_times(db: DB_dependency, data: RoomBookingsBetweenDates):
    bookings = (
        db.query(RoomBooking_DB)
        .filter((RoomBooking_DB.start_time >= data.start_time) & (RoomBooking_DB.end_time <= data.end_time))
        .all()
    )
    return bookings


@room_router.get(
    "/get_by_room/",
    response_model=list[RoomBookingRead],
    dependencies=[Permission.require("view", "Room Bookings")],
)
def get_bookings_by_room(room: ROOMS, db: DB_dependency):
    bookings = db.query(RoomBooking_DB).filter(RoomBooking_DB.room == room)
    return bookings


@room_router.delete(
    "/{booking_id}", response_model=RoomBookingRead, dependencies=[Permission.require("manage", "Room Bookings")]
)
def remove_booking(
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
    "/{booking_id}", response_model=RoomBookingRead, dependencies=[Permission.require("manage", "Room Bookings")]
)
def update_booking(
    booking_id: int, data: RoomBookingUpdate, current_user: Annotated[User_DB, Permission.member()], db: DB_dependency
):
    booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, "Room booking not found")

    for var, value in vars(data).items():
        setattr(booking, var, value) if value is not None else None

    if booking.end_time <= booking.start_time:
        raise HTTPException(400, "End time must be after start time")

    overlapping_booking = (
        db.query(RoomBooking_DB)
        .filter(
            (RoomBooking_DB.id != booking.id)
            & (RoomBooking_DB.room == booking.room)
            & (RoomBooking_DB.start_time < data.end_time)
            & (data.start_time < RoomBooking_DB.end_time)
        )
        .one_or_none()
    )

    if overlapping_booking:
        raise HTTPException(400, "The booking clashes with another booking")

    for var, value in vars(data).items():
        setattr(booking, var, value) if value else None

    db.commit()
    db.refresh(booking)
    return booking
