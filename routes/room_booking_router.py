from fastapi import APIRouter, HTTPException
from api_schemas.room_booking_schema import RoomCreate, RoomRead, RoomUpdate
from database import DB_dependency
from typing import Annotated
from sqlalchemy import or_, and_, literal
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.council_model import Council_DB
from db_models.room_booking_model import RoomBooking_DB
from helpers.types import datetime_utc
from helpers.constants import ROOMS

room_router = APIRouter()


@room_router.post("/", response_model=RoomCreate, dependencies=[Permission.require("manage", "Rooms")])
def create_booking(booking: RoomCreate, current_user: Annotated[User_DB, Permission.member()], db: DB_dependency):
    if booking.end_time <= booking.start_time:
        raise HTTPException(400, "End time must be after start time")
    illegal_booking = (
        db.query(RoomBooking_DB)
        .filter(
            and_(
                RoomBooking_DB.room_id == literal(booking.room_id),  # This makes sure we only check the same room
                or_(
                    and_(RoomBooking_DB.start_time <= booking.start_time, booking.start_time < RoomBooking_DB.end_time),
                    and_(booking.start_time < RoomBooking_DB.start_time, booking.end_time > RoomBooking_DB.start_time),
                ),  # This makes sure there is no overlap with other bookings
            )
        )
        .first()
    )
    if illegal_booking:
        raise HTTPException(400, "The booking clashes with another booking")

    council = db.query(Council_DB).filter_by(id=booking.council_id).one_or_none()
    if council is None:
        raise HTTPException(404, "Council not found")
    if booking.room_id <= 0 or booking.room_id > len(ROOMS):
        raise HTTPException(404, "Room not found")

    dictionary = {key: getattr(booking, key) for key in vars(booking)}
    db_booking = RoomBooking_DB(**dictionary, room=ROOMS[booking.room_id - 1], user_id=current_user.id)
    db.add(db_booking)
    db.commit()

    return db_booking


@room_router.get(
    "/get_booking/{booking_id}", response_model=RoomRead, dependencies=[Permission.require("view", "Rooms")]
)
def get_booking(booking_id: int, db: DB_dependency):
    booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.booking_id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, detail="Bad booking id")
    return booking


@room_router.get("/get_all", response_model=list[RoomRead], dependencies=[Permission.require("view", "Rooms")])
def get_all_bookings(db: DB_dependency):
    bookings = db.query(RoomBooking_DB).all()

    return bookings


@room_router.get(
    "/get_between_times", response_model=list[RoomRead], dependencies=[Permission.require("view", "Rooms")]
)
def get_bookings_between_times(
    db: DB_dependency,
    start_time_from: datetime_utc | None = None,
    start_time_to: datetime_utc | None = None,
    end_time_from: datetime_utc | None = None,
    end_time_to: datetime_utc | None = None,
):
    bookings = db.query(RoomBooking_DB)  # returns all bookings if no times are given

    if start_time_from is not None and start_time_to is not None:
        bookings = bookings.filter(
            and_(RoomBooking_DB.start_time >= start_time_from, RoomBooking_DB.start_time <= start_time_to)
        )  # filters out the bookings with a start time between start_time_from and start_time_to
    if end_time_from is not None and end_time_to is not None:
        bookings = bookings.filter(
            and_(RoomBooking_DB.end_time >= end_time_from, RoomBooking_DB.end_time <= end_time_to)
        )  # filters out the bookings with an end time between end_time_from and end_time_to

    return bookings


@room_router.get(
    "/get_by_room/{room_id}", response_model=list[RoomRead], dependencies=[Permission.require("view", "Rooms")]
)
def get_bookings_by_room(room_id: int, db: DB_dependency):
    bookings = db.query(RoomBooking_DB).filter(RoomBooking_DB.room_id == room_id)

    return bookings


@room_router.delete("/{booking_id}", response_model=RoomRead, dependencies=[Permission.require("manage", "Rooms")])
def remove_booking(
    booking_id: int,
    db: DB_dependency,
):
    booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.booking_id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, "Bad booking id")
    else:
        db.delete(booking)
        db.commit()
        return booking


@room_router.patch("/{booking_id}", response_model=RoomRead, dependencies=[Permission.require("manage", "Rooms")])
def update_booking(
    booking_id: int, data: RoomUpdate, current_user: Annotated[User_DB, Permission.member()], db: DB_dependency
):
    booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.booking_id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, "Bad booking id")

    if data.council_id is not None:
        council = db.query(Council_DB).filter_by(id=data.council_id).one_or_none()
        if council is None:
            raise HTTPException(404, "Council not found")
    if data.room_id is not None:
        if data.room_id <= 0 or data.room_id > len(ROOMS):
            raise HTTPException(404, "Room not found")

    for var, value in vars(data).items():
        setattr(booking, var, value) if value is not None else None
    booking.room = ROOMS[booking.room_id - 1]
    booking.user_id = current_user.id

    if booking.end_time <= booking.start_time:
        raise HTTPException(400, "End time must be after start time")

    illegal_booking = (
        db.query(RoomBooking_DB)
        .filter(
            and_(
                RoomBooking_DB.room_id == booking.room_id,  # This makes sure we only check the same room
                literal(booking_id) != RoomBooking_DB.booking_id,  # Filters out the booking we are editing
                or_(
                    and_(RoomBooking_DB.start_time <= booking.start_time, booking.start_time < RoomBooking_DB.end_time),
                    and_(booking.start_time < RoomBooking_DB.start_time, booking.end_time > RoomBooking_DB.start_time),
                ),  # This checks so that there is no overlap with other bookings before being added to the table
            )
        )
        .first()
    )

    if illegal_booking:
        raise HTTPException(400, "The booking clashes with another booking")

    db.commit()
    return booking
