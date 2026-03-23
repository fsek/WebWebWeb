from fastapi import APIRouter, HTTPException, status

from api_schemas.program_year_schema import ProgramYearCreate, ProgramYearRead, ProgramYearUpdate
from database import DB_dependency
from db_models.program_model import Program_DB
from db_models.program_year_model import ProgramYear_DB
from user.permission import Permission


program_year_router = APIRouter()


@program_year_router.get("/", response_model=list[ProgramYearRead])
def get_all_program_years(db: DB_dependency):
    return db.query(ProgramYear_DB).all()


@program_year_router.get("/{program_year_id}", response_model=ProgramYearRead)
def get_program_year(program_year_id: int, db: DB_dependency):
    program_year = db.query(ProgramYear_DB).filter_by(program_year_id=program_year_id).one_or_none()
    if program_year is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return program_year


@program_year_router.post("/", response_model=ProgramYearRead, dependencies=[Permission.require("manage", "Plugg")])
def create_program_year(data: ProgramYearCreate, db: DB_dependency):
    program = db.query(Program_DB).filter_by(program_id=data.program_id).one_or_none()
    if program is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Program not found")

    program_year = ProgramYear_DB(
        title_sv=data.title_sv,
        title_en=data.title_en,
        program_id=data.program_id,
        description_sv=data.description_sv,
        description_en=data.description_en,
    )
    db.add(program_year)
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

    program = db.query(Program_DB).filter_by(program_id=data.program_id).one_or_none()
    if program is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Program not found")

    for var, value in vars(data).items():
        # Note that we always set None values, to clear fields if the user wants to.
        setattr(program_year, var, value)

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

    db.delete(program_year)
    db.commit()
    return program_year
