from fastapi import APIRouter
from sqlalchemy import desc
from api_schemas.nollning_schema import (
    NollningCreate,
    NollningRead,
    NollningAddGroup,
    NollningDeleteMission,
    NollningGroupRead,
)
from database import DB_dependency
from db_models.nollning_model import Nollning_DB
from services.nollning_service import (
    add_g_to_nollning,
    create_nollning,
    edit_nollning,
    remove_nollning,
    delete_group_m,
    get_all_groups_in_nollning,
)
from user.permission import Permission
from routes.adventure_mission_router import adventure_mission_router
from routes.group_mission_router import group_mission_router


nollning_router = APIRouter()

nollning_router.include_router(adventure_mission_router, prefix="/{nollning_id}/missions")
nollning_router.include_router(group_mission_router, prefix="/{nollning_id}/groups/{group_id}/missions")


@nollning_router.post("/", dependencies=[Permission.require("manage", "Nollning")], response_model=NollningRead)
def post_nollning(data: NollningCreate, db: DB_dependency):
    return create_nollning(db, data)


@nollning_router.get("/", dependencies=[Permission.require("view", "Nollning")], response_model=list[NollningRead])
def get_all_nollning(db: DB_dependency):
    nollningar = db.query(Nollning_DB).order_by(desc(Nollning_DB.id))
    return nollningar


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


@nollning_router.post(
    "/{nollning_id}/groups/", dependencies=[Permission.require("manage", "Nollning")], response_model=NollningRead
)
def add_group_to_nollning(db: DB_dependency, nollning_id: int, data: NollningAddGroup):
    return add_g_to_nollning(db, nollning_id, data)


@nollning_router.get(
    "/{nollning_id}/groups/",
    dependencies=[Permission.require("view", "Nollning")],
    response_model=list[NollningGroupRead],
)
def get_all_nollning_groups(db: DB_dependency, id: int):
    return get_all_groups_in_nollning(db, id)


@nollning_router.delete(
    "/{nollning_id}/groups/{group_id}",
    dependencies=[Permission.require("manage", "Nollning")],
    response_model=NollningDeleteMission,
)
def delete_group_mission(db: DB_dependency, nollning_id: int, data: NollningDeleteMission):
    return delete_group_m(db, nollning_id, data)
