from fastapi import APIRouter, HTTPException, status

from api_schemas.program_schema import ProgramCreate, ProgramRead, ProgramUpdate
from database import DB_dependency
from db_models.program_model import Program_DB
from user.permission import Permission


program_router = APIRouter()


@program_router.get("/", response_model=list[ProgramRead])
def get_all_programs(db: DB_dependency):
    return db.query(Program_DB).all()


@program_router.get("/{program_id}", response_model=ProgramRead)
def get_program(program_id: int, db: DB_dependency):
    program = db.query(Program_DB).filter_by(program_id=program_id).one_or_none()
    if program is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return program


@program_router.post("/", response_model=ProgramRead, dependencies=[Permission.require("manage", "Plugg")])
def create_program(data: ProgramCreate, db: DB_dependency):
    program = Program_DB(
        title_sv=data.title_sv,
        title_en=data.title_en,
        description_sv=data.description_sv,
        description_en=data.description_en,
    )
    db.add(program)
    db.commit()
    db.refresh(program)
    return program


@program_router.patch("/{program_id}", response_model=ProgramRead, dependencies=[Permission.require("manage", "Plugg")])
def update_program(program_id: int, data: ProgramUpdate, db: DB_dependency):
    program = db.query(Program_DB).filter_by(program_id=program_id).one_or_none()
    if program is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    for var, value in vars(data).items():
        # Note that we always set None values, to clear fields if the user wants to.
        setattr(program, var, value)

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

    db.delete(program)
    db.commit()
    return program
