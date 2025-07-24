from fastapi import APIRouter, HTTPException
from sqlalchemy import desc
from api_schemas.group_mission_schema import GroupMissionRead
from api_schemas.nollning_schema import (
    NollningCreate,
    NollningRead,
)
from database import DB_dependency
from db_models.nollning_model import Nollning_DB
from db_models.group_mission_model import GroupMission_DB
from db_models.nollning_group_model import NollningGroup_DB
from services.nollning_service import (
    create_nollning,
    edit_nollning,
    remove_nollning,
)
from user.permission import Permission
from routes.nollning.adventure_mission_router import adventure_mission_router
from routes.nollning.groups import nollning_group_router


nollning_router = APIRouter()

nollning_router.include_router(adventure_mission_router, prefix="/{nollning_id}/missions")
nollning_router.include_router(nollning_group_router, prefix="/{nollning_id}/groups")


@nollning_router.post("/", dependencies=[Permission.require("manage", "Nollning")], response_model=NollningRead)
def post_nollning(data: NollningCreate, db: DB_dependency):
    return create_nollning(db, data)


@nollning_router.get("/", dependencies=[Permission.require("view", "Nollning")], response_model=list[NollningRead])
def get_all_nollning(db: DB_dependency):
    nollningar = db.query(Nollning_DB).order_by(desc(Nollning_DB.id))
    return nollningar


@nollning_router.get(
    "/{nollning_id}", dependencies=[Permission.require("view", "Nollning")], response_model=NollningRead
)
def get_nollning(db: DB_dependency, nollning_id: int):
    nollning = db.query(Nollning_DB).filter(Nollning_DB.id == nollning_id).one_or_none()

    if nollning is None:
        raise HTTPException(404, detail="Nollning not found")

    return nollning


@nollning_router.patch(
    "/{nollning_id}", dependencies=[Permission.require("manage", "Nollning")], response_model=NollningRead
)
def patch_nollning(db: DB_dependency, nollning_id: int, data: NollningCreate):
    return edit_nollning(db, nollning_id, data)


@nollning_router.delete(
    "/{nollning_id}", dependencies=[Permission.require("manage", "Nollning")], response_model=dict[str, str]
)
def delete_nollning(db: DB_dependency, nollning_id: int):
    return remove_nollning(db, nollning_id)


@nollning_router.get(
    "/{nollning_id}/groups/missions/",
    dependencies=[Permission.require("view", "Nollning")],
    response_model=list[GroupMissionRead],
)
def get_all_completed_missions_in_nollning(db: DB_dependency, nollning_id: int):

    completed = (
        db.query(GroupMission_DB)
        .join(NollningGroup_DB, NollningGroup_DB.id == GroupMission_DB.nollning_group_id)
        .join(Nollning_DB, Nollning_DB.id == NollningGroup_DB.nollning_id)
        .filter(Nollning_DB.id == nollning_id)
        .all()
    )

    # This will give [] even if no nollning exists for the given nollning_id

    return completed
