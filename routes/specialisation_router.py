from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_

from api_schemas.specialisation_schema import (
    SpecialisationCreate,
    SpecialisationRead,
    SpecialisationUpdate,
)
from database import DB_dependency
from db_models.specialisation_model import Specialisation_DB
from user.permission import Permission
from helpers.url_formatter import url_formatter
from services.specialisation_service import update_specialisation_course_associations, validate_course_ids


specialisation_router = APIRouter()


@specialisation_router.get("/", response_model=list[SpecialisationRead])
def get_all_specialisations(db: DB_dependency):
    return db.query(Specialisation_DB).all()


@specialisation_router.get("/by_url_title/{title}", response_model=SpecialisationRead)
def get_specialisation_by_url_title(title: str, db: DB_dependency):
    normalized_title = url_formatter(title)
    specialisation = (
        db.query(Specialisation_DB)
        .filter(
            or_(
                Specialisation_DB.title_sv_urlized == normalized_title,
                Specialisation_DB.title_en_urlized == normalized_title,
            )
        )
        .one_or_none()
    )

    if specialisation is not None:
        return specialisation

    raise HTTPException(status.HTTP_404_NOT_FOUND)


@specialisation_router.get("/{specialisation_id}", response_model=SpecialisationRead)
def get_specialisation(specialisation_id: int, db: DB_dependency):
    specialisation = db.query(Specialisation_DB).filter_by(specialisation_id=specialisation_id).one_or_none()
    if specialisation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return specialisation


@specialisation_router.post(
    "/", response_model=SpecialisationRead, dependencies=[Permission.require("manage", "Plugg")]
)
def create_specialisation(data: SpecialisationCreate, db: DB_dependency):
    missing_course_ids, duplicate_course_ids = validate_course_ids(data.course_ids, db)
    if duplicate_course_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate ids are not allowed. Duplicate course_ids: {duplicate_course_ids}",
        )
    if missing_course_ids:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Courses with ids {missing_course_ids} not found, cannot create specialisation",
        )

    normalized_sv = url_formatter(data.title_sv)
    normalized_en = url_formatter(data.title_en)

    normalized_titles = [normalized_sv, normalized_en]
    existing_title = (
        db.query(Specialisation_DB)
        .filter(
            or_(
                Specialisation_DB.title_sv_urlized.in_(normalized_titles),
                Specialisation_DB.title_en_urlized.in_(normalized_titles),
            )
        )
        .first()
    )
    if existing_title is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Specialisation title already exists")

    specialisation = Specialisation_DB(
        title_sv=data.title_sv,
        title_sv_urlized=normalized_sv,
        title_en=data.title_en,
        title_en_urlized=normalized_en,
        description_sv=data.description_sv,
        description_en=data.description_en,
    )
    db.add(specialisation)

    # Flush assigns specialisation_id without committing.
    db.flush()

    # We handle course_ids separately, since it's a many-to-many relationship.
    specialisation = update_specialisation_course_associations(specialisation, data.course_ids, db)

    db.commit()
    db.refresh(specialisation)
    return specialisation


@specialisation_router.patch(
    "/{specialisation_id}", response_model=SpecialisationRead, dependencies=[Permission.require("manage", "Plugg")]
)
def update_specialisation(specialisation_id: int, data: SpecialisationUpdate, db: DB_dependency):
    specialisation = db.query(Specialisation_DB).filter_by(specialisation_id=specialisation_id).one_or_none()
    if specialisation is None:
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
            detail=f"Courses with ids {missing_course_ids} not found, cannot update specialisation",
        )

    normalized_sv = url_formatter(data.title_sv)
    normalized_en = url_formatter(data.title_en)

    normalized_titles = [normalized_sv, normalized_en]
    existing_title = (
        db.query(Specialisation_DB)
        .filter(Specialisation_DB.specialisation_id != specialisation_id)
        .filter(
            or_(
                Specialisation_DB.title_sv_urlized.in_(normalized_titles),
                Specialisation_DB.title_en_urlized.in_(normalized_titles),
            )
        )
        .first()
    )
    if existing_title is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Specialisation title already exists")

    for var, value in vars(data).items():
        if var != "course_ids":
            # Note that we always set None values, to clear fields if the user wants to.
            setattr(specialisation, var, value)

    specialisation.title_sv_urlized = normalized_sv
    specialisation.title_en_urlized = normalized_en

    # We handle course_ids separately, since it's a many-to-many relationship.
    specialisation = update_specialisation_course_associations(specialisation, data.course_ids, db)

    db.commit()
    db.refresh(specialisation)
    return specialisation


@specialisation_router.delete(
    "/{specialisation_id}", response_model=SpecialisationRead, dependencies=[Permission.require("manage", "Plugg")]
)
def delete_specialisation(specialisation_id: int, db: DB_dependency):
    specialisation = db.query(Specialisation_DB).filter_by(specialisation_id=specialisation_id).one_or_none()
    if specialisation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(specialisation)
    db.commit()
    return specialisation
