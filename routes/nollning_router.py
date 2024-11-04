from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import desc
from api_schemas.nollning_schema import NollningCreate, NollningRead
from database import DB_dependency
from db_models.news_model import News_DB
from db_models.nollning_model import Nollning_DB
from db_models.user_model import User_DB
from user.permission import Permission

nollning_router = APIRouter()


@nollning_router.post("/", response_model=NollningRead)
def post_nollning(data: NollningCreate, db: DB_dependency):
    nollning = Nollning_DB(name=data.name, description=data.description)
    db.add(nollning)
    db.commit()
    return nollning


@nollning_router.get("/all", response_model=list[NollningRead])
def get_all_nollning(db: DB_dependency):
    nollningar = db.query(Nollning_DB).order_by(desc(Nollning_DB.id))
    return nollningar
