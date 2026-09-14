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
    "/admin/levels",
    response_model=EncloseMooseLevelRead,
    dependencies=[Permission.require("manage", "EncloseMoose")],
)
def admin_create_level(data: EncloseMooseLevelCreate, db: DB_dependency):
    level = level_create(data)

    db.add(level)
    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(400, detail="Some string is too long")

    level.show_spoilers = True  # pyright: ignore

    return level


@enclose_moose_router.get(
    "/admin/levels/{level_id}",
    response_model=EncloseMooseLevelRead,
    dependencies=[Permission.require("manage", "EncloseMoose")],
)
def admin_get_level(level_id: int, db: DB_dependency):
    level = db.get(EncloseMooseLevel_DB, level_id)
    if level is None:
        raise HTTPException(404, detail=f'No level with level_id "{level_id}" exists')

    level.show_spoilers = True  # pyright: ignore

    return level


@enclose_moose_router.get(
    "/admin/levels",
    response_model=list[EncloseMooseLevelRead],
    dependencies=[Permission.require("manage", "EncloseMoose")],
)
def admin_get_all_levels(db: DB_dependency):
    levels = db.query(EncloseMooseLevel_DB).order_by(EncloseMooseLevel_DB.release_date).all()

    for level in levels:
        level.show_spoilers = True  # pyright: ignore

    return levels


@enclose_moose_router.patch(
    "/admin/levels/{level_id}",
    response_model=EncloseMooseLevelRead,
    dependencies=[Permission.require("manage", "EncloseMoose")],
)
def admin_update_level(level_id: int, data: EncloseMooseLevelUpdate, db: DB_dependency):
    level = db.get(EncloseMooseLevel_DB, level_id)
    if level is None:
        raise HTTPException(404, detail=f'No level with level_id "{level_id}" exists')

    updated_level = level_update(level, data)
    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(400, detail="Some string is too long")

    updated_level.show_spoilers = True  # pyright: ignore

    return updated_level


@enclose_moose_router.delete(
    "/admin/levels/{level_id}",
    response_model=EncloseMooseLevelRead,
    dependencies=[Permission.require("manage", "EncloseMoose")],
)
def admin_delete_level(level_id: int, db: DB_dependency):
    level = db.get(EncloseMooseLevel_DB, level_id)
    if level is None:
        raise HTTPException(404, detail=f'No level with level_id "{level_id}" exists')

    db.delete(level)
    db.commit()

    level.show_spoilers = True  # pyright: ignore

    return level


@enclose_moose_router.get(
    "/admin/submissions/{level_id}",
    response_model=list[EncloseMooseSubmissionRead],
    dependencies=[Permission.require("manage", "EncloseMoose")],
)
def admin_get_all_level_submissions(
    level_id: int,
    db: DB_dependency,
):
    submissions = db.query(EncloseMooseSubmission_DB).filter(EncloseMooseSubmission_DB.level_id == level_id).all()

    return submissions


# Non-admin routes
@enclose_moose_router.get("/levels/{level_id}", response_model=EncloseMooseLevelRead)
def get_level(level_id: int, me: Annotated[User_DB, Permission.member()], db: DB_dependency):
    date_today = datetime.now(ZoneInfo("Europe/Stockholm")).date()
    level = (
        db.query(EncloseMooseLevel_DB)
        .filter(EncloseMooseLevel_DB.release_date <= date_today, EncloseMooseLevel_DB.level_id == level_id)
        .one_or_none()
    )
    if level is None:
        raise HTTPException(404, detail=f'No level with level_id "{level_id}" exists')

    submission = db.get(EncloseMooseSubmission_DB, (level_id, me.id))
    level.player_submission = submission  # pyright: ignore
    level.show_spoilers = submission is not None  # pyright: ignore

    return level


@enclose_moose_router.get("/levels", response_model=list[EncloseMooseLevelRead])
def get_all_levels(me: Annotated[User_DB, Permission.member()], db: DB_dependency):
    date_today = datetime.now(ZoneInfo("Europe/Stockholm")).date()

    results = (
        db.query(EncloseMooseLevel_DB, EncloseMooseSubmission_DB)
        .outerjoin(
            EncloseMooseSubmission_DB,
            (EncloseMooseSubmission_DB.level_id == EncloseMooseLevel_DB.level_id)
            & (EncloseMooseSubmission_DB.player_id == me.id),
        )
        .filter(EncloseMooseLevel_DB.release_date <= date_today)
        .order_by(EncloseMooseLevel_DB.release_date)
        .all()
    )

    levels: list[EncloseMooseLevel_DB] = []
    for level, submission in results:
        level.player_submission = submission
        level.show_spoilers = submission is not None  # pyright: ignore
        levels.append(level)

    return levels


@enclose_moose_router.post("/submissions/{level_id}", response_model=EncloseMooseLevelRead)
def submit_solution(
    level_id: int,
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

    level.player_submission = db_submission  # pyright: ignore
    level.show_spoilers = True  # pyright: ignore

    return level


@enclose_moose_router.get("/submissions/{level_id}", response_model=EncloseMooseSubmissionRead)
def get_submission(
    level_id: int,
    me: Annotated[User_DB, Permission.member()],
    db: DB_dependency,
):
    submission = db.get(EncloseMooseSubmission_DB, (level_id, me.id))
    if submission is None:
        raise HTTPException(404, detail="No submission exists for this player and level")

    return submission


@enclose_moose_router.get("/submissions", response_model=list[EncloseMooseSubmissionRead])
def get_all_submissions(
    me: Annotated[User_DB, Permission.member()],
    db: DB_dependency,
):
    submissions = db.query(EncloseMooseSubmission_DB).filter(EncloseMooseSubmission_DB.player_id == me.id).all()

    return submissions
