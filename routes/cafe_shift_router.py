from fastapi import APIRouter, HTTPException, status
from database import DB_dependency
from db_models.cafe_shift_model import CafeShift_DB
from api_schemas.event_schemas import EventCreate, EventRead, EventUpdate  # change to cafeshift
from services.event_service import create_new_event, delete_event, update_event  # change to cafeshift
from user.permission import Permission
from datetime import datetime

cafe_shift_router = APIRouter()


@cafe_shift_router.get("/", response_model=list[CafeShiftRead])
def view_all_shifts(db: DB_dependency):
    shifts = db.query(CafeShift_DB).all()
    return shifts


@cafe_shift_router.get("/{shift_id}", response_model=CafeShiftRead)
def view_shift(shift_id: int, db: DB_dependency):
    shift = db.query(CafeShift_DB).filter_by(id=shift_id).one_or_none()
    if shift is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return shift


@cafe_shift_router.get("/", response_model=list[CafeShiftRead])
def view_shifts_between_dates(start_date: datetime, end_date: datetime, db: DB_dependency):
    shifts = (
        db.query(CafeShift_DB)
        .all.filter(Permission_DB.action == perm_data.action, Permission_DB.target == perm_data.target)
        .filter()
    )
