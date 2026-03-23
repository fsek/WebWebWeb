from fastapi import APIRouter, HTTPException, status

from api_schemas.specialisation_schema import SpecialisationCreate, SpecialisationRead, SpecialisationUpdate
from database import DB_dependency
from db_models.program_model import Program_DB
from db_models.specialisation_model import Specialisation_DB
from user.permission import Permission


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
    program = db.query(Program_DB).filter_by(program_id=data.program_id).one_or_none()
    if program is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Program not found")

    specialisation = Specialisation_DB(
        title_sv=data.title_sv,
        title_en=data.title_en,
        program_id=data.program_id,
        description_sv=data.description_sv,
        description_en=data.description_en,
    )
    db.add(specialisation)
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

    program = db.query(Program_DB).filter_by(program_id=data.program_id).one_or_none()
    if program is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Program not found")

    for var, value in vars(data).items():
        # Note that we always set None values, to clear fields if the user wants to.
        setattr(specialisation, var, value)

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
