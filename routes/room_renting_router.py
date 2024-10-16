from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from api_schemas.room_booking_schema import RoomCreate, RoomRead, RoomUpdate
from api_schemas.room_booking_schema import RoomRead
from database import DB_dependency
from typing import Annotated
from sqlalchemy import or_, and_
from db_models.council_model import Council_DB
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.room_booking_model import RoomBooking_DB
from helpers.types import datetime

room_router = APIRouter()


@room_router.get("/", response_model=list[RoomRead], dependencies=[Permission.member()])
def get_all_booking(db: DB_dependency):
    bookings = db.query(RoomBooking_DB).all()
    return bookings


@room_router.get(
    "/{booking_id}", response_model=RoomRead, dependencies=[Permission.require("view", "Room"), Permission.member()]
)
def get_booking(booking_id: int, db: DB_dependency):
    booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.booking_id == booking_id).first()
    if booking:
        return booking
    raise HTTPException(status.HTTP_400_BAD_REQUEST)


@room_router.get("/", response_model=list[RoomRead], dependencies=[Permission.member()])
def get_upcoming_bookings(db: DB_dependency):
    a_week_ahead = datetime.today().replace(day=datetime.today().day + 7)
    bookings = (
        db.query(RoomBooking_DB)
        .having(RoomBooking_DB.start_time > datetime.today())
        .having(RoomBooking_DB.start_time < a_week_ahead)
    )
    return bookings


@room_router.post("/", response_model=RoomCreate, dependencies=[Permission.require("manage", "Room")])
def create_booking(booking: RoomCreate, current_user: Annotated[User_DB, Permission.member()], current_council: Annotated[Council_DB, Permission.member()], db: DB_dependency):
    if booking.end_time < booking.start_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    illegal_booking = (
        db.query(RoomBooking_DB)
        .filter(
            or_(
                and_(booking.start_time >= RoomBooking_DB.start_time, booking.start_time < RoomBooking_DB.end_time),
                and_(booking.end_time > RoomBooking_DB.start_time, booking.end_time <= RoomBooking_DB.end_time),
                and_(booking.start_time <= RoomBooking_DB.start_time, booking.end_time >= RoomBooking_DB.end_time),
            )
        )
        .first()
    )
    if illegal_booking:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    
    #council = db.query(Council_DB).filter(Council_DB.name.lower() == current_council.lower()).one_or_none()
    if not current_council:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    
    db_booking = RoomBooking_DB(
        start_time=booking.start_time,
        end_time=booking.end_time,
        description=booking.description,
        user_id=current_user.id,
        council_id=current_council.id
    )
    db.add(db_booking)
    db.commit()
    return db_booking


@room_router.delete("/{booking_id}", response_model=RoomRead)
def remove_booking(
    booking_id: int,
    current_user: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Car")],
    db: DB_dependency,
):
    room_booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.booking_id == booking_id).first()
    if room_booking is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    if (room_booking.user == current_user) or manage_permission:
        db.delete(room_booking)
        db.commit()
        return room_booking

    raise HTTPException(status.HTTP_401_UNAUTHORIZED)


@room_router.patch("/{booking_id}", response_model=RoomRead)
def update_booking(
    booking_id: int,
    data: RoomUpdate,
    current_user: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Room")],
    db: DB_dependency,
):
    room_booking = db.query(RoomBooking_DB).filter(RoomBooking_DB.booking_id == booking_id).first()
    if room_booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if (room_booking.user != current_user) and (not manage_permission):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    illegal_booking = (
        db.query(RoomBooking_DB)
        .filter(
            or_(
                and_(data.start_time >= RoomBooking_DB.start_time, data.start_time < RoomBooking_DB.end_time),
                and_(data.end_time > RoomBooking_DB.start_time, data.end_time <= RoomBooking_DB.end_time),
                and_(data.start_time <= RoomBooking_DB.start_time, data.end_time >= RoomBooking_DB.end_time),
            )  # This checks so that there is no overlap with other bookings before being added to the table
        )
        .first()
    )

    if illegal_booking:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    if data.description is not None:
        room_booking.description = data.description

    if data.start_time is not None:
        room_booking.start_time = data.start_time
    if data.end_time is not None:
        room_booking.end_time = data.end_time

    db.commit()
    return room_booking
