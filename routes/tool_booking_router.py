from fastapi import APIRouter, HTTPException
from sqlalchemy import and_
from api_schemas.tool_booking_schema import (
    ToolBookingCreate,
    ToolBookingRead,
    ToolBookingUpdate,
)
from database import DB_dependency
from typing import Annotated
from db_models.tool_model import Tool_DB
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.tool_booking_model import ToolBooking_DB
from helpers.types import datetime_utc
from services import tool_booking_service


tool_booking_router = APIRouter()


@tool_booking_router.post(
    "/", response_model=ToolBookingRead, dependencies=[Permission.require("manage", "ToolBookings")]
)
def create_tool_booking(
    data: ToolBookingCreate,
    current_user: Annotated[User_DB, Permission.require("manage", "ToolBookings")],
    db: DB_dependency,
):
    tool = db.query(Tool_DB).filter(Tool_DB.id == data.tool_id).one_or_none()
    if tool is None:
        raise HTTPException(404, "Tool not found")

    if data.amount <= 0:
        raise HTTPException(400, "Amount must be positive")

    if data.end_time <= data.start_time:
        raise HTTPException(400, "End time must be after start time")

    overlapping_bookings = (
        db.query(ToolBooking_DB)
        .filter(
            and_(
                ToolBooking_DB.tool_id == data.tool_id,
                ToolBooking_DB.start_time < data.end_time,
                data.start_time < ToolBooking_DB.end_time,
            )
        )
        .all()
    )

    booked_amount = tool_booking_service.max_booked(overlapping_bookings)

    if booked_amount + data.amount > tool.amount:
        raise HTTPException(400, "Not enough tools available at that time")

    tool_booking = ToolBooking_DB(
        tool_id=data.tool_id,
        amount=data.amount,
        start_time=data.start_time,
        end_time=data.end_time,
        user_id=current_user.id,
        description=data.description,
    )

    db.add(tool_booking)

    db.commit()

    return tool_booking


@tool_booking_router.get(
    "/get_booking/{booking_id}",
    response_model=ToolBookingRead,
    dependencies=[Permission.require("view", "ToolBookings")],
)
def get_tool_booking(booking_id: int, db: DB_dependency):
    booking = db.query(ToolBooking_DB).filter(ToolBooking_DB.id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, "Tool booking not found")
    return booking


@tool_booking_router.get(
    "/get_all",
    response_model=list[ToolBookingRead],
    dependencies=[Permission.require("view", "ToolBookings")],
)
def get_all_tool_bookings(db: DB_dependency):
    bookings = db.query(ToolBooking_DB).all()
    return bookings


@tool_booking_router.get(
    "/get_between_times",
    response_model=list[ToolBookingRead],
    dependencies=[Permission.require("view", "ToolBookings")],
)
def get_tool_bookings_between_times(db: DB_dependency, start_time: datetime_utc, end_time: datetime_utc):
    bookings = (
        db.query(ToolBooking_DB)
        .filter(and_(ToolBooking_DB.start_time >= start_time, ToolBooking_DB.end_time <= end_time))
        .all()
    )
    return bookings


@tool_booking_router.get(
    "/get_by_tool/",
    response_model=list[ToolBookingRead],
    dependencies=[Permission.require("view", "ToolBookings")],
)
def get_tool_bookings_by_tool(tool_id: int, db: DB_dependency):
    tool = db.query(Tool_DB).filter(Tool_DB.id == tool_id).one_or_none()
    if tool is None:
        raise HTTPException(404, "Tool not found")
    bookings = tool.bookings
    return bookings


@tool_booking_router.delete(
    "/{booking_id}", response_model=ToolBookingRead, dependencies=[Permission.require("manage", "ToolBookings")]
)
def remove_tool_booking(
    booking_id: int,
    db: DB_dependency,
):
    booking = db.query(ToolBooking_DB).filter(ToolBooking_DB.id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, "Tool booking not found")

    db.delete(booking)
    db.commit()
    return booking


@tool_booking_router.patch(
    "/{booking_id}", response_model=ToolBookingRead, dependencies=[Permission.require("manage", "ToolBookings")]
)
def update_tool_booking(
    booking_id: int,
    data: ToolBookingUpdate,
    db: DB_dependency,
):
    tool_booking = db.query(ToolBooking_DB).filter(ToolBooking_DB.id == booking_id).one_or_none()
    if tool_booking is None:
        raise HTTPException(404, "Tool booking not found")

    if data.start_time is None:
        data.start_time = tool_booking.start_time
    if data.end_time is None:
        data.end_time = tool_booking.end_time
    if data.end_time <= data.start_time:
        raise HTTPException(400, "End time must be after start time")

    if data.amount is not None:
        if data.amount <= 0:
            raise HTTPException(400, "Amount must be positive")

        overlapping_bookings = (
            db.query(ToolBooking_DB)
            .filter(
                and_(
                    ToolBooking_DB.id != booking_id,
                    ToolBooking_DB.tool_id == tool_booking.tool_id,
                    ToolBooking_DB.start_time < data.end_time,
                    data.start_time < ToolBooking_DB.end_time,
                )
            )
            .all()
        )

        booked_amount = tool_booking_service.max_booked(overlapping_bookings)

        if booked_amount + data.amount > tool_booking.tool.amount:
            raise HTTPException(400, "Not enough tools available at that time")

    for var, value in vars(data).items():
        setattr(tool_booking, var, value) if value else None

    db.commit()
    db.refresh(tool_booking)
    return tool_booking
