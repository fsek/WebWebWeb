from fastapi import APIRouter
from api_schemas.adventure_mission_schema import AdventureMissionCreate, AdventureMissionRead
from database import DB_dependency
from services.adventure_mission_service import (
    create_adventure_mission,
    edit_adventure_mission,
    find_adventure_mission,
    remove_adventure_mission,
    find_all_adventure_missions,
)
from user.permission import Permission

adventure_mission_router = APIRouter()


@adventure_mission_router.post(
    "/", dependencies=[Permission.require("manage", "Adventure Missions")], response_model=AdventureMissionRead
)
def post_adventure_mission(db: DB_dependency, data: AdventureMissionCreate):
    return create_adventure_mission(db, data)


@adventure_mission_router.get("/all", response_model=list[AdventureMissionRead])
def get_all_adventure_missions(db: DB_dependency):
    return find_all_adventure_missions(db)


@adventure_mission_router.get("/{id}", response_model=AdventureMissionRead)
def get_adventure_mission(db: DB_dependency, id: int):
    return find_adventure_mission(db, id)


@adventure_mission_router.delete(
    "/delete/{id}",
    dependencies=[Permission.require("manage", "Adventure Missions")],
    response_model=AdventureMissionRead,
)
def delete_adventure_mission(db: DB_dependency, id: int):
    return remove_adventure_mission(db, id)


@adventure_mission_router.patch(
    "/patch/{id}",
    dependencies=[Permission.require("manage", "Adventure Missions")],
    response_model=AdventureMissionRead,
)
def patch_adventure_mission(db: DB_dependency, id: int, data: AdventureMissionCreate):
    return edit_adventure_mission(db, id, data)
