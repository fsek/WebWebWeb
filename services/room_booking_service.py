from fastapi import HTTPException
from api_schemas.room_booking_schemas import (
    RoomBookingCreate,
)
from database import DB_dependency
from typing import Annotated
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.council_model import Council_DB
from db_models.room_booking_model import RoomBooking_DB


def create_new_room_booking(
    data: RoomBookingCreate, current_user: Annotated[User_DB, Permission.member()], db: DB_dependency
):
    if data.end_time <= data.start_time:
        raise HTTPException(400, "End time must be after start time")

    overlapping_booking = (
        db.query(RoomBooking_DB)
        .filter(
            (RoomBooking_DB.room == data.room)
            & (RoomBooking_DB.start_time < data.end_time)
            & (data.start_time < RoomBooking_DB.end_time)
        )
        .first()
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

    return room_booking
