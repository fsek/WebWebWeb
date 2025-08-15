from fastapi import APIRouter, HTTPException, status
from datetime import UTC, datetime, timedelta, time
from zoneinfo import ZoneInfo

# from sqlalchemy import null
from typing import Annotated
from database import DB_dependency
from db_models.user_model import User_DB
from db_models.cafe_shift_model import CafeShift_DB
from api_schemas.cafe_schemas import (
    CafeShiftCreate,
    CafeShiftRead,
    CafeShiftUpdate,
    CafeViewBetweenDates,
    CafeShiftCreateMulti,
)
from user.permission import Permission

cafe_shift_router = APIRouter()


@cafe_shift_router.get("/view-shifts", dependencies=[Permission.member()], response_model=list[CafeShiftRead])
def view_all_shifts(db: DB_dependency):
    shifts = db.query(CafeShift_DB).all()
    return shifts


@cafe_shift_router.get("/{shift_id}", dependencies=[Permission.member()], response_model=CafeShiftRead)
def view_shift(shift_id: int, db: DB_dependency):
    shift = db.query(CafeShift_DB).filter_by(id=shift_id).one_or_none()
    if shift is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return shift


# Var tvungen att göra en fuling och göra detta till en POST för att kunna skicka med en JSON body. Det var problem med att parsa datetimes om de skickades med som fält.
@cafe_shift_router.post("/view-between-dates", dependencies=[Permission.member()], response_model=list[CafeShiftRead])
def view_shifts_between_dates(data: CafeViewBetweenDates, db: DB_dependency):
    shifts = (
        db.query(CafeShift_DB)
        .filter(CafeShift_DB.starts_at >= data.start_date, CafeShift_DB.ends_at <= data.end_date)
        .all()
    )

    return shifts


@cafe_shift_router.post("/", dependencies=[Permission.require("manage", "Cafe")], response_model=CafeShiftRead)
def create_shift(data: CafeShiftCreate, db: DB_dependency):
    start = data.starts_at
    end = data.ends_at
    if end <= start:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Start time must be before end")

    if start < datetime.now(UTC):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Shift cannot be in the past, goofball.")

    shift = CafeShift_DB(starts_at=start, ends_at=end)
    db.add(shift)
    db.commit()

    return shift


@cafe_shift_router.post(
    "/multi", dependencies=[Permission.require("manage", "Cafe")], response_model=list[CafeShiftRead]
)
def create_multiple_shifts(data: CafeShiftCreateMulti, db: DB_dependency):
    shifts: list[CafeShift_DB] = []

    # Define shift times based on configuration
    shift_times = {
        "full": [(8, 10), (10, 13), (13, 15), (15, 17)],
        "morning": [(8, 10), (10, 13)],
        "afternoon": [(13, 15), (15, 17)],
    }

    current_week = data.startWeekStart.date()
    end_week = data.endWeekStart.date()

    if current_week > end_week:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid week range")

    if current_week < datetime.now(UTC).date():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Cannot create shifts in the past")

    if end_week - current_week > timedelta(weeks=4):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Cannot create shifts for more than 4 weeks at a time")

    local_tz = ZoneInfo("Europe/Stockholm")

    sanity_index = 0

    while current_week <= end_week and sanity_index < 100:
        sanity_index += 1
        # Create shifts for Monday (0) through Friday (4)
        for day_offset in range(5):  # Monday to Friday
            shift_date = current_week + timedelta(days=day_offset)

            # Create shifts for the selected configuration
            for start_hour, end_hour in shift_times[data.configuration]:
                # build local time at Stockholm tz, then convert to UTC
                start_local = datetime.combine(shift_date, time(start_hour), tzinfo=local_tz)
                end_local = datetime.combine(shift_date, time(end_hour), tzinfo=local_tz)
                start_time = start_local.astimezone(UTC)
                end_time = end_local.astimezone(UTC)

                # Skip shifts in the past
                if start_time < datetime.now(UTC):
                    continue

                # Yes, we do want two shifts for each slot (two workers)
                shift = CafeShift_DB(starts_at=start_time, ends_at=end_time)
                shifts.append(shift)
                db.add(shift)
                shift = CafeShift_DB(starts_at=start_time, ends_at=end_time)
                shifts.append(shift)
                db.add(shift)

        # Move to next week
        current_week += timedelta(weeks=1)

    db.commit()
    return shifts


@cafe_shift_router.delete(
    "/{shift_id}", dependencies=[Permission.require("manage", "Cafe")], status_code=status.HTTP_204_NO_CONTENT
)
def delete_shift(shift_id: int, db: DB_dependency):
    shift = db.query(CafeShift_DB).filter_by(id=shift_id).one_or_none()
    if shift is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(shift)
    db.commit()
    return


@cafe_shift_router.patch(
    "/update/{shift_id}", dependencies=[Permission.require("manage", "Cafe")], response_model=CafeShiftRead
)
def update_shift(shift_id: int, data: CafeShiftUpdate, db: DB_dependency):
    shift = db.query(CafeShift_DB).filter_by(id=shift_id).one_or_none()
    if shift is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    temp_start = shift.starts_at
    temp_end = shift.ends_at
    if data.starts_at is not None:
        temp_start = data.starts_at
    if data.ends_at is not None:
        temp_end = data.ends_at
    if temp_end <= temp_start:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Start time must be before end")

    shift.starts_at = temp_start
    shift.ends_at = temp_end

    if data.user_id is not None:
        user = db.query(User_DB).filter_by(id=data.user_id).one_or_none()
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        shift.user_id = data.user_id
        shift.user = user
    else:  # This goes slightly against standards but makes the frontend way easier to create
        shift.user = None
        shift.user_id = None

    db.commit()
    return shift


@cafe_shift_router.patch("/sign-up/{shift_id}", response_model=CafeShiftRead)
def signup_to_shift(shift_id: int, user: Annotated[User_DB, Permission.member()], db: DB_dependency):
    shift = db.query(CafeShift_DB).filter_by(id=shift_id).one_or_none()
    if shift is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if shift.user is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Another member is already signed up")

    shift.user = user
    db.commit()
    return shift


@cafe_shift_router.patch("/sign-off/{shift_id}", response_model=CafeShiftRead)
def signoff_from_shift(
    shift_id: int,
    user: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Cafe")],
    db: DB_dependency,
):
    shift = db.query(CafeShift_DB).filter_by(id=shift_id).one_or_none()
    if shift is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if shift.user_id != user.id and manage_permission == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Cannot sign off another member")

    shift.user = None
    shift.user_id = None
    db.commit()
    return shift
