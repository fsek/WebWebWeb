from fastapi import HTTPException, status
from api_schemas.car_booking_schema import CarBookingCreate, CarBookingUpdate
from db_models.council_model import Council_DB
from database import DB_dependency
from typing import Annotated
from sqlalchemy import or_, and_, literal
from user.permission import Permission
from db_models.user_model import User_DB
from db_models.car_booking_model import CarBooking_DB
from datetime import UTC, datetime
from db_models.car_block_model import CarBlock_DB
from mailer import bilf_mailer


def is_user_blocked(user_id: int, db: DB_dependency) -> bool:
    block = db.query(CarBlock_DB).filter(CarBlock_DB.user_id == user_id).first()
    return block is not None


def overlap_query_create(
    booking: CarBookingCreate,
    db: DB_dependency,
):
    result = (
        db.query(CarBooking_DB)
        .filter(
            and_(
                or_(
                    and_(booking.start_time >= CarBooking_DB.start_time, booking.start_time < CarBooking_DB.end_time),
                    and_(booking.end_time > CarBooking_DB.start_time, booking.end_time <= CarBooking_DB.end_time),
                    and_(booking.start_time <= CarBooking_DB.start_time, booking.end_time >= CarBooking_DB.end_time),
                ),
            )
        )
        .first()
    )

    if result:
        return True
    return False


def overlap_query_update(booking: CarBookingUpdate, booking_id: int, db: DB_dependency):
    result = (
        db.query(CarBooking_DB)
        .filter(
            and_(
                or_(  # This mess below makes sure stuff doesn't break if start_time or end_time is None
                    *(
                        (
                            and_(
                                booking.start_time >= CarBooking_DB.start_time,
                                booking.start_time < CarBooking_DB.end_time,
                            ),
                        )
                        if booking.start_time is not None
                        else ()
                    ),
                    *(
                        (
                            and_(
                                booking.end_time > CarBooking_DB.start_time,
                                booking.end_time <= CarBooking_DB.end_time,
                            ),
                        )
                        if booking.end_time is not None
                        else ()
                    ),
                    *(
                        (
                            and_(
                                booking.start_time <= CarBooking_DB.start_time,
                                booking.end_time >= CarBooking_DB.end_time,
                            ),
                        )
                        if (booking.start_time is not None and booking.end_time is not None)
                        else ()
                    ),
                ),  # This checks so that there is no overlap with other bookings before being added to the table
                # filters out the booking we are editing
                literal(booking_id) != CarBooking_DB.booking_id,
            )
        )
        .first()
    )

    if result:
        return True


def create_new_booking(
    data: CarBookingCreate,
    db: DB_dependency,
    current_user: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Car")],
) -> CarBooking_DB:
    booking_confirmed = True  # Default to confirmed unless conditions below change it
    if data.end_time < data.start_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Booking end time cannot be before start time.")
    if data.start_time == data.end_time:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Booking start time cannot be equal to end time.")
    booking_overlaps = overlap_query_create(
        booking=data,
        db=db,
    )
    if booking_overlaps:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Booking overlaps with another booking.")
    if data.start_time < datetime.now(UTC):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Booking start time cannot be in the past.")

    if not manage_permission:
        # Unconfirm booking between 17:00 and 08:00
        if data.start_time.hour < 8 or data.start_time.hour >= 17:
            booking_confirmed = False
        if data.end_time.hour < 8 or data.end_time.hour >= 17:
            booking_confirmed = False
        # Unconfirm booking on weekends
        if data.start_time.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            booking_confirmed = False

    # Require council_id if not personal booking
    if not data.personal and data.council_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Council ID is required for non-personal bookings.")

    # Remove council_id if personal booking
    if data.personal and data.council_id is not None:
        data.council_id = None

    # Check if the council_id is valid
    if data.council_id is not None:
        council = db.query(Council_DB).filter(Council_DB.id == data.council_id).one_or_none()
        if council is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid council ID.")

    # Disallow regular users from booking cars for other councils
    if not manage_permission and data.council_id is not None:  # For safety, we don't care if it is a personal booking
        if data.council_id not in [post.council_id for post in current_user.posts]:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, detail="You do not have permission to book cars for this council."
            )

    db_booking = CarBooking_DB(
        start_time=data.start_time,
        end_time=data.end_time,
        user_id=current_user.id,
        description=data.description,
        confirmed=booking_confirmed,
        personal=data.personal,
        council_id=data.council_id,
    )
    db.add(db_booking)
    db.commit()

    bilf_mailer.bilf_mailer(db_booking)

    return db_booking


def booking_update(
    booking_id: int,
    data: CarBookingUpdate,
    current_user: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Car")],
    db: DB_dependency,
) -> CarBooking_DB:

    car_booking = db.query(CarBooking_DB).filter(CarBooking_DB.booking_id == booking_id).first()
    if car_booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Booking not found.")
    if (car_booking.user != current_user) and (not manage_permission):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="You do not have permission to update this booking.")

    if data.confirmed is not None:
        booking_confirmed = data.confirmed  # default to updated value, fallback to previous value
    else:
        booking_confirmed = car_booking.confirmed

    # Automagically assume the user wants the booking confirmed, they should not have manual control unlike admins
    if not manage_permission and booking_confirmed == False:
        booking_confirmed = True

    # only check for illegal overlap if new times are provided
    if data.start_time is not None or data.end_time is not None:
        # Use new values if provided, otherwise use existing values
        check_start_time = data.start_time if data.start_time is not None else car_booking.start_time
        check_end_time = data.end_time if data.end_time is not None else car_booking.end_time

        if check_start_time >= check_end_time:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail="Booking start time cannot be after nor equal to end time."
            )

        booking_overlaps = overlap_query_update(
            booking=data,
            booking_id=booking_id,
            db=db,
        )

        if booking_overlaps:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Booking overlaps with another booking.")

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

    # Remove council_id if personal booking
    if data.personal and data.council_id is not None:
        data.council_id = None

    # Check if the council_id is valid
    if data.council_id is not None:
        council = db.query(Council_DB).filter(Council_DB.id == data.council_id).one_or_none()
        if council is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid council ID.")

    # Disallow regular users from booking cars for other councils
    if not manage_permission and data.council_id is not None:
        if data.council_id not in [post.council_id for post in current_user.posts]:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, detail="You do not have permission to book cars for this council."
            )

    # Require a council_id if the booking changes from personal to council
    if (
        data.personal is not None
        and data.personal is False
        and car_booking.personal is True
        and data.council_id is None
    ):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Council ID is required when making non-personal booking."
        )

    car_booking.confirmed = booking_confirmed

    for attr in ["description", "start_time", "end_time", "personal", "council_id"]:
        value = getattr(data, attr, None)
        if value is not None:
            setattr(car_booking, attr, value)

    db.commit()

    return car_booking
