from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from api_schemas.council_schema import CouncilCreate, CouncilRead
from db_models.council_model import Council_DB
from user.permission import Permission
from database import DB_dependency
from db_models.council_model import Council_DB
from db_models.user_model import User_DB


council_router = APIRouter()


@council_router.post("/", response_model=CouncilRead, dependencies=[Permission.require("manage", "Council")])
def create_council(data: CouncilCreate, db: DB_dependency):
    council = db.query(Council_DB).filter_by(name=data.name).one_or_none()
    if council is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Council already exists")
    council = Council_DB(name=data.name, description=data.description)
    db.add(council)
    db.commit()
    return council


@council_router.get("/", response_model=list[CouncilRead])
def get_all_councils(current_user: Annotated[User_DB, Permission.member()], db: DB_dependency):
    return db.query(Council_DB).all()


@council_router.get("/{council_id}", response_model=CouncilRead)
def get_council(current_user: Annotated[User_DB, Permission.member()], council_id: int, db: DB_dependency):
    council = db.query(Council_DB).filter_by(id=council_id).one_or_none()
    if council is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return council
