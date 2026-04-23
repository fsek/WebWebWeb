from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from api_schemas.program_schema import ProgramCreate, ProgramRead, ProgramUpdate
from database import DB_dependency
from db_models.program_model import Program_DB
from user.permission import Permission
from helpers.url_formatter import url_formatter
from services.program_service import (
    update_program_specialisation_associations,
    validate_specialisation_ids,
)
from services.plugg_cleanup_service import collect_orphaned_associated_img_path_after_detach, remove_files


program_router = APIRouter()


@program_router.get("/", response_model=list[ProgramRead])
def get_all_programs(db: DB_dependency):
    return db.query(Program_DB).all()


@program_router.get("/by_url_title/{title}", response_model=ProgramRead)
def get_program_by_url_title(title: str, db: DB_dependency):
    normalized_title = url_formatter(title)
    program = (
        db.query(Program_DB)
        .filter(or_(Program_DB.title_sv_urlized == normalized_title, Program_DB.title_en_urlized == normalized_title))
        .one_or_none()
    )

    if program is not None:
        return program

    raise HTTPException(status.HTTP_404_NOT_FOUND)


@program_router.get("/{program_id}", response_model=ProgramRead)
def get_program(program_id: int, db: DB_dependency):
    program = db.query(Program_DB).filter_by(program_id=program_id).one_or_none()
    if program is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return program


@program_router.post("/", response_model=ProgramRead, dependencies=[Permission.require("manage", "Plugg")])
def create_program(data: ProgramCreate, db: DB_dependency):
    missing_specialisation_ids, duplicate_specialisation_ids = validate_specialisation_ids(data.specialisation_ids, db)
    if duplicate_specialisation_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate ids are not allowed. Duplicate specialisation_ids: {duplicate_specialisation_ids}",
        )
    if missing_specialisation_ids:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Specialisations with ids {missing_specialisation_ids} not found, cannot create program",
        )

    # Check for conflicting titles using url-formatter so we can fetch by title later

    normalized_sv = url_formatter(data.title_sv)
    normalized_en = url_formatter(data.title_en)

    normalized_titles = [normalized_sv, normalized_en]
    existing_title = (
        db.query(Program_DB)
        .filter(
            or_(
                Program_DB.title_sv_urlized.in_(normalized_titles),
                Program_DB.title_en_urlized.in_(normalized_titles),
            )
        )
        .first()
    )

    if existing_title is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Program title already exists")

    program = Program_DB(
        title_sv=data.title_sv,
        title_sv_urlized=normalized_sv,
        title_en=data.title_en,
        title_en_urlized=normalized_en,
        description_sv=data.description_sv,
        description_en=data.description_en,
    )
    db.add(program)

    # Flush assigns program_id without committing.
    db.flush()

    # We handle specialisation_ids separately, since it's a many-to-many relationship.
    program = update_program_specialisation_associations(program, data.specialisation_ids, db)

    db.commit()
    db.refresh(program)
    return program


@program_router.patch("/{program_id}", response_model=ProgramRead, dependencies=[Permission.require("manage", "Plugg")])
def update_program(program_id: int, data: ProgramUpdate, db: DB_dependency):
    program = db.query(Program_DB).filter_by(program_id=program_id).one_or_none()
    if program is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    missing_specialisation_ids, duplicate_specialisation_ids = validate_specialisation_ids(data.specialisation_ids, db)
    if duplicate_specialisation_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate ids are not allowed. Duplicate specialisation_ids: {duplicate_specialisation_ids}",
        )
    if missing_specialisation_ids:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Specialisations with ids {missing_specialisation_ids} not found, cannot update program",
        )

    normalized_sv = url_formatter(data.title_sv)
    normalized_en = url_formatter(data.title_en)

    # Check for conflicting titles using url-formatter so we can fetch by title later. Ignore the current program when checking.
    normalized_titles = [normalized_sv, normalized_en]
    existing_title = (
        db.query(Program_DB)
        .filter(Program_DB.program_id != program_id)
        .filter(
            or_(
                Program_DB.title_sv_urlized.in_(normalized_titles),
                Program_DB.title_en_urlized.in_(normalized_titles),
            )
        )
        .first()
    )
    if existing_title is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Program title already exists")

    for var, value in vars(data).items():
        if var != "specialisation_ids":
            # Note that we always set None values, to clear fields if the user wants to.
            setattr(program, var, value)

    # We require title fields so these will always exist and should now be updated
    program.title_sv_urlized = normalized_sv
    program.title_en_urlized = normalized_en

    # We handle specialisation_ids separately, since it's a many-to-many relationship.
    program = update_program_specialisation_associations(program, data.specialisation_ids, db)

    db.commit()
    db.refresh(program)
    return program


@program_router.delete(
    "/{program_id}", response_model=ProgramRead, dependencies=[Permission.require("manage", "Plugg")]
)
def delete_program(program_id: int, db: DB_dependency):
    program = db.query(Program_DB).filter_by(program_id=program_id).one_or_none()
    if program is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    # Fixing proper handling of program_years is too much work so let's just forbid deletion if
    # there are program_years associated.
    if program.program_years:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete program with associated program years. Delete them first.",
        )

    files_to_remove: list[str] = []

    try:
        files_to_remove.extend(collect_orphaned_associated_img_path_after_detach(db, program))
        db.delete(program)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(500, detail="Could not delete program and all related resources")

    remove_files(files_to_remove)
    return program
