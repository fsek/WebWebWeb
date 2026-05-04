from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from api_schemas.program_year_schema import ProgramYearCreate, ProgramYearRead, ProgramYearUpdate
from database import DB_dependency
from db_models.program_model import Program_DB
from db_models.program_year_model import ProgramYear_DB
from user.permission import Permission
from helpers.url_formatter import url_formatter
from services.program_year_service import update_program_year_course_associations, validate_course_ids
from services.plugg_cleanup_service import collect_orphaned_associated_img_path_after_detach, remove_files


program_year_router = APIRouter()


@program_year_router.get("/", response_model=list[ProgramYearRead])
def get_all_program_years(db: DB_dependency):
    return db.query(ProgramYear_DB).all()


@program_year_router.get("/by_program/{program_id}", response_model=list[ProgramYearRead])
def get_program_years_by_program(program_id: int, db: DB_dependency):
    program = db.query(Program_DB).filter_by(program_id=program_id).one_or_none()
    if program is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Program not found")

    return db.query(ProgramYear_DB).filter_by(program_id=program_id).all()


@program_year_router.get("/by_url_title/{program_title}/{program_year_title}", response_model=ProgramYearRead)
def get_program_year_by_url_title(program_title: str, program_year_title: str, db: DB_dependency):
    normalized_program_title = url_formatter(program_title)
    normalized_program_year_title = url_formatter(program_year_title)
    program = (
        db.query(Program_DB)
        .filter(
            or_(
                Program_DB.title_sv_urlized == normalized_program_title,
                Program_DB.title_en_urlized == normalized_program_title,
            ),
        )
        .one_or_none()
    )

    if program is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Program not found")

    program_year = (
        db.query(ProgramYear_DB)
        .filter(
            ProgramYear_DB.program_id == program.program_id,
            or_(
                ProgramYear_DB.title_sv_urlized == normalized_program_year_title,
                ProgramYear_DB.title_en_urlized == normalized_program_year_title,
            ),
        )
        .one_or_none()
    )

    if program_year is not None:
        return program_year

    raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Program year not found")


@program_year_router.get("/{program_year_id}", response_model=ProgramYearRead)
def get_program_year(program_year_id: int, db: DB_dependency):
    program_year = db.query(ProgramYear_DB).filter_by(program_year_id=program_year_id).one_or_none()
    if program_year is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return program_year


@program_year_router.post("/", response_model=ProgramYearRead, dependencies=[Permission.require("manage", "Plugg")])
def create_program_year(data: ProgramYearCreate, db: DB_dependency):
    missing_course_ids, duplicate_course_ids = validate_course_ids(data.course_ids, db)
    if duplicate_course_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate ids are not allowed. Duplicate course_ids: {duplicate_course_ids}",
        )
    if missing_course_ids:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Courses with ids {missing_course_ids} not found, cannot create program year",
        )

    program = db.query(Program_DB).filter_by(program_id=data.program_id).one_or_none()
    if program is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Program not found")

    normalized_sv = url_formatter(data.title_sv)
    normalized_en = url_formatter(data.title_en)

    normalized_titles = [normalized_sv, normalized_en]
    existing_title = (
        db.query(ProgramYear_DB)
        .filter_by(program_id=data.program_id)
        .filter(
            or_(
                ProgramYear_DB.title_sv_urlized.in_(normalized_titles),
                ProgramYear_DB.title_en_urlized.in_(normalized_titles),
            )
        )
        .first()
    )
    if existing_title is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Program year title already exists")

    program_year = ProgramYear_DB(
        title_sv=data.title_sv,
        title_sv_urlized=normalized_sv,
        title_en=data.title_en,
        title_en_urlized=normalized_en,
        program_id=data.program_id,
        description_sv=data.description_sv,
        description_en=data.description_en,
    )
    db.add(program_year)

    # Flush assigns program_year_id without committing.
    db.flush()

    # We handle course_ids separately, since it's a many-to-many relationship.
    program_year = update_program_year_course_associations(program_year, data.course_ids, db)

    db.commit()
    db.refresh(program_year)
    return program_year


@program_year_router.patch(
    "/{program_year_id}", response_model=ProgramYearRead, dependencies=[Permission.require("manage", "Plugg")]
)
def update_program_year(program_year_id: int, data: ProgramYearUpdate, db: DB_dependency):
    program_year = db.query(ProgramYear_DB).filter_by(program_year_id=program_year_id).one_or_none()
    if program_year is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    missing_course_ids, duplicate_course_ids = validate_course_ids(data.course_ids, db)
    if duplicate_course_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate ids are not allowed. Duplicate course_ids: {duplicate_course_ids}",
        )
    if missing_course_ids:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Courses with ids {missing_course_ids} not found, cannot update program year",
        )

    program = db.query(Program_DB).filter_by(program_id=data.program_id).one_or_none()
    if program is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Program not found")

    normalized_sv = url_formatter(data.title_sv)
    normalized_en = url_formatter(data.title_en)

    normalized_titles = [normalized_sv, normalized_en]
    existing_title = (
        db.query(ProgramYear_DB)
        .filter(ProgramYear_DB.program_year_id != program_year_id)
        .filter_by(program_id=data.program_id)
        .filter(
            or_(
                ProgramYear_DB.title_sv_urlized.in_(normalized_titles),
                ProgramYear_DB.title_en_urlized.in_(normalized_titles),
            )
        )
        .first()
    )
    if existing_title is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Program year title already exists")

    for var, value in vars(data).items():
        if var != "course_ids":
            # Note that we always set None values, to clear fields if the user wants to.
            setattr(program_year, var, value)

    program_year.title_sv_urlized = normalized_sv
    program_year.title_en_urlized = normalized_en

    # We handle course_ids separately, since it's a many-to-many relationship.
    program_year = update_program_year_course_associations(program_year, data.course_ids, db)

    db.commit()
    db.refresh(program_year)
    return program_year


@program_year_router.delete(
    "/{program_year_id}", response_model=ProgramYearRead, dependencies=[Permission.require("manage", "Plugg")]
)
def delete_program_year(program_year_id: int, db: DB_dependency):
    program_year = db.query(ProgramYear_DB).filter_by(program_year_id=program_year_id).one_or_none()
    if program_year is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    files_to_remove: list[str] = []

    try:
        files_to_remove.extend(collect_orphaned_associated_img_path_after_detach(db, program_year))
        db.delete(program_year)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(500, detail="Could not delete program year and all related resources")

    remove_files(files_to_remove)
    return program_year
