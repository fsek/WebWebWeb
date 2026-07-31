import os
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, HTTPException, Request
from typing import Annotated
from sqlalchemy.exc import DataError, IntegrityError
from api_schemas.enclose_moose_level_schema import (
    EncloseMooseLevelRead,
    EncloseMooseLevelCreate,
    EncloseMooseLevelUpdate,
)
from api_schemas.enclose_moose_submission_schema import EncloseMooseSubmissionRead, EncloseMooseSubmissionCreate
from user.permission import Permission
from database import DB_dependency
from db_models.user_model import User_DB
from db_models.enclose_moose_level_model import EncloseMooseLevel_DB
from db_models.enclose_moose_submission_model import EncloseMooseSubmission_DB
from services.enclose_moose_service import level_create, level_update, solution_submit

ENCLOSE_MOOSE_SECRET = os.getenv("ENCLOSE_MOOSE_TOKEN")

enclose_moose_router = APIRouter()


# Admin routes
@enclose_moose_router.post(
    "/admin", response_model=EncloseMooseLevelRead, dependencies=[Permission.require("manage", "EncloseMoose")]
)
def admin_create_level(data: EncloseMooseLevelCreate, db: DB_dependency):
    level = level_create(data)

    db.add(level)
    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(400, detail="Some string is too long")
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, detail=f'A level with level_id "{data.level_id}" already exists')

    return level


@enclose_moose_router.get(
    "/admin/{level_id}",
    response_model=EncloseMooseLevelRead,
    dependencies=[Permission.require("manage", "EncloseMoose")],
)
def admin_get_level(level_id: str, db: DB_dependency):
    level = db.get(EncloseMooseLevel_DB, level_id)
    if level is None:
        raise HTTPException(404, detail=f'No level with level_id "{level_id}" exists')

    return level


@enclose_moose_router.get(
    "/admin", response_model=list[EncloseMooseLevelRead], dependencies=[Permission.require("manage", "EncloseMoose")]
)
def admin_get_all_levels(db: DB_dependency):
    levels = db.query(EncloseMooseLevel_DB).order_by(EncloseMooseLevel_DB.release_date).all()

    return levels


@enclose_moose_router.patch(
    "/admin/{level_id}",
    response_model=EncloseMooseLevelRead,
    dependencies=[Permission.require("manage", "EncloseMoose")],
)
def admin_update_level(level_id: str, data: EncloseMooseLevelUpdate, db: DB_dependency):
    level = db.get(EncloseMooseLevel_DB, level_id)
    if level is None:
        raise HTTPException(404, detail=f'No level with level_id "{level_id}" exists')

    updated_level = level_update(level, data)
    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(400, detail="Some string is too long")

    return updated_level


@enclose_moose_router.delete(
    "/admin/{level_id}",
    response_model=EncloseMooseLevelRead,
    dependencies=[Permission.require("manage", "EncloseMoose")],
)
def admin_delete_level(level_id: str, db: DB_dependency):
    level = db.get(EncloseMooseLevel_DB, level_id)
    if level is None:
        raise HTTPException(404, detail=f'No level with level_id "{level_id}" exists')

    db.delete(level)
    db.commit()

    return level


# Non-admin routes
@enclose_moose_router.get("/{level_id}", response_model=EncloseMooseLevelRead, dependencies=[Permission.member()])
def get_level(level_id: str, db: DB_dependency):
    date_today = datetime.now(ZoneInfo("Europe/Stockholm")).date()
    level = (
        db.query(EncloseMooseLevel_DB)
        .filter(EncloseMooseLevel_DB.release_date <= date_today, EncloseMooseLevel_DB.level_id == level_id)
        .one_or_none()
    )
    if level is None:
        raise HTTPException(404, detail=f'No level with level_id "{level_id}" exists')

    return level


@enclose_moose_router.get("/", response_model=list[EncloseMooseLevelRead], dependencies=[Permission.member()])
def get_all_levels(db: DB_dependency):
    date_today = datetime.now(ZoneInfo("Europe/Stockholm")).date()

    levels = (
        db.query(EncloseMooseLevel_DB)
        .filter(EncloseMooseLevel_DB.release_date <= date_today)
        .order_by(EncloseMooseLevel_DB.release_date)
        .all()
    )

    return levels


@enclose_moose_router.post("/{level_id}/submit", response_model=EncloseMooseSubmissionRead)
def submit_solution(
    level_id: str,
    submission: EncloseMooseSubmissionCreate,
    me: Annotated[User_DB, Permission.member()],
    request: Request,
    db: DB_dependency,
):
    token = request.headers.get("enclose-moose-token")
    if ENCLOSE_MOOSE_SECRET != token:
        raise HTTPException(401, detail="Invalid enclose-moose-token")

    date_today = datetime.now(ZoneInfo("Europe/Stockholm")).date()
    level = (
        db.query(EncloseMooseLevel_DB)
        .filter(EncloseMooseLevel_DB.release_date <= date_today, EncloseMooseLevel_DB.level_id == level_id)
        .one_or_none()
    )
    if level is None:
        raise HTTPException(404, detail=f'No level with level_id "{level_id}" exists')

    db_submission = solution_submit(level, submission.player_solution, me.id)
    db.add(db_submission)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            409,
            detail="The player has already submitted a solution to this level",
        )

    return db_submission


@enclose_moose_router.get("/{level_id}/submit", response_model=EncloseMooseSubmissionRead)
def get_submission(
    level_id: str,
    me: Annotated[User_DB, Permission.member()],
    db: DB_dependency,
):
    submission = db.get(EncloseMooseSubmission_DB, (level_id, me.id))
    if submission is None:
        raise HTTPException(404, detail="No submission exists for this player and level")

    return submission
