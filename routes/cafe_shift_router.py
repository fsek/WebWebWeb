from fastapi import APIRouter, HTTPException, status

# from sqlalchemy import null
from typing import Annotated
from database import DB_dependency
from db_models.user_model import User_DB
from db_models.cafe_shift_model import CafeShift_DB
from api_schemas.cafe_schemas import CafeShiftCreate, CafeShiftRead, CafeShiftUpdate
from user.permission import Permission
from helpers.types import datetime_utc
from datetime import UTC, datetime

cafe_shift_router = APIRouter()


@cafe_shift_router.get("/", response_model=list[CafeShiftRead])
def view_all_shifts(db: DB_dependency):
    shifts = db.query(CafeShift_DB).all()
    return shifts


@cafe_shift_router.get("/{shift_id}", response_model=CafeShiftRead)
def view_shift(shift_id: int, db: DB_dependency):
    shift = db.query(CafeShift_DB).filter_by(shift_id=shift_id).one_or_none()
    if shift is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return shift


@cafe_shift_router.get("/", response_model=list[CafeShiftRead])
def view_shifts_between_dates(start_date: datetime_utc, end_date: datetime_utc, db: DB_dependency):
    shifts = db.query(CafeShift_DB).filter(CafeShift_DB.starts_at >= start_date, CafeShift_DB.ends_at <= end_date)
    if shifts.count() == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="No shifts between selected dates")
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


@cafe_shift_router.delete(
    "/{shift_id}", dependencies=[Permission.require("manage", "Cafe")], status_code=status.HTTP_204_NO_CONTENT
)
def remove(shift_id: int, db: DB_dependency):
    shift = db.query(CafeShift_DB).filter_by(shift_id=shift_id).one_or_none()
    if shift is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(shift)
    db.commit()
    return


@cafe_shift_router.patch(
    "/{shift_id}", dependencies=[Permission.require("manage", "Cafe")], response_model=CafeShiftRead
)
def update(shift_id: int, data: CafeShiftUpdate, db: DB_dependency):
    shift = db.query(CafeShift_DB).filter_by(shift_id=shift_id).one_or_none()
    if shift is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if data.starts_at is not None:
        shift.starts_at = data.starts_at
    if data.ends_at is not None:
        shift.ends_at = data.ends_at
    if data.user_id is not None:
        user = db.query(User_DB).filter_by(id=data.user_id).one_or_none()
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        shift.user_id = data.user_id
        shift.user = user

    db.commit()
    return shift


@cafe_shift_router.patch("/{shift_id}", response_model=CafeShiftRead)
def sign_up(shift_id: int, user: Annotated[User_DB, Permission.member()], db: DB_dependency):
    shift = db.query(CafeShift_DB).filter_by(shift_id=shift_id).one_or_none()
    if shift is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if shift.user is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Another member is already signed up")

    shift.user = user
    db.commit()
    return shift


@cafe_shift_router.patch("/{shift_id}", response_model=CafeShiftRead)
def sign_off(shift_id: int, user: Annotated[User_DB, Permission.member()], db: DB_dependency):
    shift = db.query(CafeShift_DB).filter_by(shift_id=shift_id).one_or_none()
    if shift is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if shift.user_id != user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Cannot sign off a nother member")

    shift.user = None
    shift.user_id = None
    db.commit()
    return shift


@cafe_shift_router.patch(
    "/{shift_id}", dependencies=[Permission.require("manage", "Cafe")], response_model=CafeShiftRead
)
def sign_off_other(shift_id: int, user: Annotated[User_DB, Permission.member()], db: DB_dependency):
    shift = db.query(CafeShift_DB).filter_by(shift_id=shift_id).one_or_none()
    if shift is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    shift.user = None
    shift.user_id = None
    db.commit()
    return shift
