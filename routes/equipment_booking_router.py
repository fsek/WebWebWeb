from fastapi import APIRouter, HTTPException
from sqlalchemy import and_
from api_schemas.equipment_booking_schema import (
    EquipmentBookingCreate,
    EquipmentBookingRead,
    EquipmentBookingUpdate,
    SimpleEquipmentBookingRead,
)
from database import DB_dependency
from typing import Annotated
from db_models.equipment_model import Equipment_DB
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.equipment_booking_model import EquipmentBooking_DB
from helpers.types import datetime_utc
from services import equipment_booking_service

equipment_booking_router = APIRouter()


@equipment_booking_router.post("/", response_model=EquipmentBookingRead)
def create_equipment_booking(
    data: EquipmentBookingCreate,
    current_user: Annotated[User_DB, Permission.require("manage", "EquipmentBookings")],
    db: DB_dependency,
):
    equipment = db.query(Equipment_DB).filter(Equipment_DB.id == data.equipment_id).one_or_none()
    if equipment is None:
        raise HTTPException(404, "Equipment not found")

    if data.amount <= 0:
        raise HTTPException(400, "Amount must be positive")

    if data.end_time <= data.start_time:
        raise HTTPException(400, "End time must be after start time")

    overlapping_bookings = (
        db.query(EquipmentBooking_DB)
        .filter(
            and_(
                EquipmentBooking_DB.equipment_id == data.equipment_id,
                EquipmentBooking_DB.start_time < data.end_time,
                data.start_time < EquipmentBooking_DB.end_time,
            )
        )
        .all()
    )

    booked_amount = equipment_booking_service.max_booked(overlapping_bookings)

    if booked_amount + data.amount > equipment.amount:
        raise HTTPException(400, "Not enough equipment available at that time")

    equipment_booking = EquipmentBooking_DB(
        equipment_id=data.equipment_id,
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
    response_model=EquipmentBookingRead,
    dependencies=[Permission.require("view", "EquipmentBookings")],
)
def get_tool_booking(booking_id: int, db: DB_dependency):
    booking = db.query(EquipmentBooking_DB).filter(EquipmentBooking_DB.id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, "Equipment booking not found")
    return booking


@tool_booking_router.get(
    "/get_simple_booking/{booking_id}",
    response_model=SimpleEquipmentBookingRead,
)
def get_public_tool_booking(booking_id: int, db: DB_dependency, current_user: Annotated[User_DB, Permission.member()]):
    booking = db.query(EquipmentBooking_DB).filter(EquipmentBooking_DB.id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, "Tool booking not found")
    return booking


@tool_booking_router.get(
    "/get_all",
    response_model=list[EquipmentBookingRead],
    dependencies=[Permission.require("view", "EquipmentBookings")],
)
def get_all_tool_bookings(db: DB_dependency):
    bookings = db.query(EquipmentBooking_DB).all()
    return bookings


@tool_booking_router.get(
    "/get_simple_all",
    response_model=list[SimpleEquipmentBookingRead],
)
def get_public_all_tool_bookings(db: DB_dependency, current_user: Annotated[User_DB, Permission.member()]):
    bookings = db.query(EquipmentBooking_DB).all()
    return bookings


@tool_booking_router.get(
    "/get_between_times",
    response_model=list[EquipmentBookingRead],
    dependencies=[Permission.require("view", "EquipmentBookings")],
)
def get_tool_bookings_between_times(db: DB_dependency, start_time: datetime_utc, end_time: datetime_utc):
    bookings = (
        db.query(EquipmentBooking_DB)
        .filter(and_(EquipmentBooking_DB.start_time < end_time, start_time < EquipmentBooking_DB.end_time))
        .all()
    )
    return bookings


@tool_booking_router.get(
    "/get_simple_between_times",
    response_model=list[SimpleEquipmentBookingRead],
)
def get_public_tool_bookings_between_times(
    db: DB_dependency,
    start_time: datetime_utc,
    end_time: datetime_utc,
    current_user: Annotated[User_DB, Permission.member()],
):
    bookings = (
        db.query(EquipmentBooking_DB)
        .filter(and_(EquipmentBooking_DB.start_time < end_time, start_time < EquipmentBooking_DB.end_time))
        .all()
    )
    return bookings


@tool_booking_router.get(
    "/get_by_tool/",
    response_model=list[EquipmentBookingRead],
    dependencies=[Permission.require("view", "EquipmentBookings")],
)
def get_tool_bookings_by_tool(tool_id: int, db: DB_dependency):
    tool = db.query(Equipment_DB).filter(Equipment_DB.id == tool_id).one_or_none()
    if tool is None:
        raise HTTPException(404, "Equipment not found")
    bookings = tool.bookings
    return bookings


@tool_booking_router.get(
    "/get_simple_by_tool/",
    response_model=list[SimpleEquipmentBookingRead],
)
def get_public_tool_bookings_by_tool(
    tool_id: int, db: DB_dependency, current_user: Annotated[User_DB, Permission.member()]
):
    tool = db.query(Equipment_DB).filter(Equipment_DB.id == tool_id).one_or_none()
    if tool is None:
        raise HTTPException(404, "Equipment not found")
    bookings = tool.bookings
    return bookings


@tool_booking_router.delete(
    "/{booking_id}",
    response_model=EquipmentBookingRead,
    dependencies=[Permission.require("manage", "EquipmentBookings")],
)
def remove_tool_booking(
    booking_id: int,
    db: DB_dependency,
):
    booking = db.query(EquipmentBooking_DB).filter(EquipmentBooking_DB.id == booking_id).one_or_none()
    if booking is None:
        raise HTTPException(404, "Equipment booking not found")

    db.delete(booking)
    db.commit()
    return booking


@tool_booking_router.patch(
    "/{booking_id}",
    response_model=EquipmentBookingRead,
    dependencies=[Permission.require("manage", "EquipmentBookings")],
)
def update_tool_booking(
    booking_id: int,
    data: EquipmentBookingUpdate,
    db: DB_dependency,
):
    tool_booking = db.query(EquipmentBooking_DB).filter(EquipmentBooking_DB.id == booking_id).one_or_none()
    if tool_booking is None:
        raise HTTPException(404, "Equipment booking not found")

    if data.start_time is None:
        data.start_time = tool_booking.start_time
    if data.end_time is None:
        data.end_time = tool_booking.end_time
    if data.end_time <= data.start_time:
        raise HTTPException(400, "End time must be after start time")

    if data.amount is None:
        data.amount = tool_booking.amount
    elif data.amount <= 0:
        raise HTTPException(400, "Amount must be positive")

    if (
        data.amount != tool_booking.amount
        or data.start_time != tool_booking.start_time
        or data.end_time != tool_booking.end_time
    ):
        overlapping_bookings = (
            db.query(EquipmentBooking_DB)
            .filter(
                and_(
                    EquipmentBooking_DB.id != booking_id,
                    EquipmentBooking_DB.tool_id == tool_booking.tool_id,
                    EquipmentBooking_DB.start_time < data.end_time,
                    data.start_time < EquipmentBooking_DB.end_time,
                )
            )
            .all()
        )

        booked_amount = tool_booking_service.max_booked(overlapping_bookings)

        if booked_amount + data.amount > tool_booking.tool.amount:
            raise HTTPException(400, "Not enough tools available at that time")

    for var, value in vars(data).items():
        # description may be explicitly set to None or "", other fields are only updated if given
        if var == "description":
            if "description" in data.model_fields_set:
                tool_booking.description = value
        else:
            setattr(tool_booking, var, value)

    db.commit()
    db.refresh(tool_booking)
    return tool_booking
