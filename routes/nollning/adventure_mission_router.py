from fastapi import APIRouter
from api_schemas.adventure_mission_schema import AdventureMissionCreate, AdventureMissionRead
from database import DB_dependency
from services.adventure_mission_service import (
    create_adventure_mission_,
    edit_adventure_mission_,
    find_adventure_mission,
    remove_adventure_mission,
    find_all_adventure_missions,
)
from user.permission import Permission

adventure_mission_router = APIRouter()


@adventure_mission_router.post(
    "/", dependencies=[Permission.require("manage", "Adventure Missions")], response_model=AdventureMissionRead
)
def create_adventure_mission(db: DB_dependency, data: AdventureMissionCreate):
    return create_adventure_mission_(db, data)


@adventure_mission_router.get("/", response_model=list[AdventureMissionRead])
def get_all_adventure_missions_in_nollning(db: DB_dependency, nollning_id: int):
    return find_all_adventure_missions(db, nollning_id)


@adventure_mission_router.get("/{mission_id}", response_model=AdventureMissionRead)
def get_adventure_mission(db: DB_dependency, mission_id: int):
    return find_adventure_mission(db, mission_id)


@adventure_mission_router.delete(
    "/{mission_id}",
    dependencies=[Permission.require("manage", "Adventure Missions")],
    response_model=AdventureMissionRead,
)
def delete_adventure_mission(db: DB_dependency, mission_id: int):
    return remove_adventure_mission(db, mission_id)


@adventure_mission_router.patch(
    "/{mission_id}",
    dependencies=[Permission.require("manage", "Adventure Missions")],
    response_model=AdventureMissionRead,
)
def edit_adventure_mission(db: DB_dependency, mission_id: int, data: AdventureMissionCreate):
    return edit_adventure_mission_(db, mission_id, data)
