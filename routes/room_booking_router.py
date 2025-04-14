from fastapi import APIRouter, HTTPException
from api_schemas.room_booking_schema import RoomCreate, RoomRead, RoomUpdate
from database import DB_dependency
from typing import Annotated
from sqlalchemy import or_, and_, literal
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.room_model import RoomBooking_DB
from helpers.types import datetime_utc

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
                    (RoomBooking_DB.start_time <= booking.start_time < RoomBooking_DB.end_time),
                    and_(booking.start_time <= RoomBooking_DB.start_time, booking.end_time > RoomBooking_DB.start_time),
                ),  # This makes sure there is no overlap with other bookings
            )
        )
        .first()
    )
    if illegal_booking:
        raise HTTPException(400, "The booking clashes with another booking")

    dictionary = {key: getattr(booking, key) for key in vars(booking)}
    db_booking = RoomBooking_DB(**dictionary, user_id=current_user.id)
    db.add(db_booking)
    db.commit()

    return db_booking


@room_router.get("/", response_model=list[RoomRead], dependencies=[Permission.require("view", "Rooms")])
def get_bookings(db: DB_dependency, start_time: datetime_utc | None = None, end_time: datetime_utc | None = None):
    if start_time is None and end_time is None:
        bookings = db.query(RoomBooking_DB).all()
    elif start_time is None:
        bookings = db.query(RoomBooking_DB).filter(RoomBooking_DB.end_time <= end_time)
    elif end_time is None:
        bookings = db.query(RoomBooking_DB).filter(start_time <= RoomBooking_DB.start_time)
    else:
        bookings = db.query(RoomBooking_DB).filter(
            and_(RoomBooking_DB.start_time <= start_time, end_time <= RoomBooking_DB.end_time)
        )

    return bookings


@room_router.get("/{booking_id}", response_model=RoomRead, dependencies=[Permission.require("view", "Rooms")])
def get_booking(booking_id: int, db: DB_dependency):
    booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.booking_id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, detail="Bad booking id")
    return booking


@room_router.delete("/{booking_id}", response_model=RoomRead, dependencies=[Permission.require("manage", "Rooms")])
def remove_booking(
    booking_id: int,
    current_user: Annotated[User_DB, Permission.member()],
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

    for var, value in vars(data).items():
        setattr(booking, var, value) if value is not None else None
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
                    (RoomBooking_DB.start_time <= booking.start_time < RoomBooking_DB.end_time),
                    and_(booking.start_time <= RoomBooking_DB.start_time, booking.end_time > RoomBooking_DB.start_time),
                ),  # This checks so that there is no overlap with other bookings before being added to the table
            )
        )
        .first()
    )

    if illegal_booking:
        raise HTTPException(400, "The booking clashes with another booking")

    db.commit()
    return booking
