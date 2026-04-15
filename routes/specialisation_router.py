from fastapi import APIRouter, HTTPException, status

from api_schemas.specialisation_schema import (
    SpecialisationCreate,
    SpecialisationRead,
    SpecialisationUpdate,
)
from database import DB_dependency
from db_models.specialisation_model import Specialisation_DB
from user.permission import Permission
from services.specialisation_service import update_specialisation_program_associations, validate_program_ids


specialisation_router = APIRouter()


@specialisation_router.get("/", response_model=list[SpecialisationRead])
def get_all_specialisations(db: DB_dependency):
    return db.query(Specialisation_DB).all()


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
    if not data.program_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="At least one program_id must be provided to create a specialisation",
        )

    # We have to validate before creating the specialisation,
    # otherwise we might end up with orphaned specialisations
    missing_program_ids, duplicate_program_ids = validate_program_ids(data.program_ids, db)
    if duplicate_program_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate ids are not allowed. Duplicate program_ids: {duplicate_program_ids}",
        )
    if missing_program_ids:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Programs with ids {missing_program_ids} not found, cannot create specialisation",
        )

    specialisation = Specialisation_DB(
        title_sv=data.title_sv,
        title_en=data.title_en,
        description_sv=data.description_sv,
        description_en=data.description_en,
    )
    db.add(specialisation)
    # Flush assigns specialisation_id without committing
    db.flush()

    # We handle the program_ids separately, since it's a many-to-many relationship.
    specialisation = update_specialisation_program_associations(specialisation, data.program_ids, db)

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

    if not data.program_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="At least one program_id must be provided to update a specialisation",
        )

    # We have to validate before updating the specialisation
    missing_program_ids, duplicate_program_ids = validate_program_ids(data.program_ids, db)
    if duplicate_program_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate ids are not allowed. Duplicate program_ids: {duplicate_program_ids}",
        )
    if missing_program_ids:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Programs with ids {missing_program_ids} not found, cannot update specialisation",
        )

    for var, value in vars(data).items():
        if var != "program_ids":
            # Note that we always set None values, to clear fields if the user wants to.
            setattr(specialisation, var, value)

    # We handle the program_ids separately, since it's a many-to-many relationship.
    specialisation = update_specialisation_program_associations(specialisation, data.program_ids, db)

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
