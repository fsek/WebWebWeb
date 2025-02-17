from fastapi import APIRouter, HTTPException, status
from api_schemas.council_schema import CouncilCreate, CouncilRead
from db_models.council_model import Council_DB
from user.permission import Permission
from database import DB_dependency

council_router = APIRouter()


@council_router.post("/", response_model=CouncilRead, dependencies=[Permission.require("manage", "Council")])
def create_council(data: CouncilCreate, db: DB_dependency):
    council = db.query(Council_DB).filter_by(name=data.name).one_or_none()
    if council is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Council already exists")
    council = Council_DB(name=data.name)
    db.add(council)
    db.commit()
    return council


@council_router.get("/", response_model=list[CouncilRead], dependencies=[Permission.require("manage", "Council")])
def get_all_councils(db: DB_dependency):
    return db.query(Council_DB).all()
