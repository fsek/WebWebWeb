from fastapi import APIRouter

from api_schemas.nollning_schema import NollningAddGroup, NollningGroupRead, NollningRead
from database import DB_dependency
from services.nollning_service import add_g_to_nollning, get_all_groups_in_nollning
from user.permission import Permission
from .group_mission_router import group_mission_router

nollning_group_router = APIRouter()

nollning_group_router.include_router(group_mission_router, prefix="/{group_id}/missions")


@nollning_group_router.post("/", dependencies=[Permission.require("manage", "Nollning")], response_model=NollningRead)
def add_group_to_nollning(db: DB_dependency, nollning_id: int, data: NollningAddGroup):
    return add_g_to_nollning(db, nollning_id, data)


@nollning_group_router.get(
    "/",
    dependencies=[Permission.require("view", "Nollning")],
    response_model=list[NollningGroupRead],
)
def get_all_nollning_groups(db: DB_dependency, id: int):
    return get_all_groups_in_nollning(db, id)
