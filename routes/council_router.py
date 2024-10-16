from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from api_schemas.base_schema import BaseSchema
from database import DB_dependency
from db_models.council_model import Council_DB
from api_schemas.council_schema import CouncilRead
from user.permission import Permission
from sqlalchemy.exc import DataError

council_router = APIRouter()


@council_router.get("/", response_model=list[CouncilRead])
def get_all_councils(db: DB_dependency):
    all_councils = db.query(Council_DB).all()
    return all_councils
