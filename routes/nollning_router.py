from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import desc
from api_schemas.nollning_schema import NollningCreate, NollningRead
from database import DB_dependency
from db_models.news_model import News_DB
from db_models.nollning_model import Nollning_DB
from db_models.user_model import User_DB
from services.nollning_service import create_nollning, edit_nollning, remove_nollning
from user.permission import Permission

nollning_router = APIRouter()


@nollning_router.post("/", dependencies=[Permission.require("manage", "Nollning")], response_model=NollningRead)
def post_nollning(data: NollningCreate, db: DB_dependency):
    return create_nollning(db, data)


@nollning_router.get("/all", dependencies=[Permission.require("view", "Nollning")], response_model=list[NollningRead])
def get_all_nollning(db: DB_dependency):
    nollningar = db.query(Nollning_DB).order_by(desc(Nollning_DB.id))
    return nollningar


@nollning_router.patch(
    "/patch/{id}", dependencies=[Permission.require("manage", "Nollning")], response_model=NollningRead
)
def patch_nollning(db: DB_dependency, id: int, data: NollningCreate):
    return edit_nollning(db, id, data)


@nollning_router.delete(
    "/delete/{id}", dependencies=[Permission.require("manage", "Nollning")], response_model=dict[str, str]
)
def delete_nollning(db: DB_dependency, id: int):
    return remove_nollning(db, id)
