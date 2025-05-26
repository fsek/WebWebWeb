from fastapi import APIRouter, HTTPException
from sqlalchemy import and_, desc
from api_schemas.group_schema import GroupRead
from api_schemas.nollning_schema import (
    NollningCreate,
    NollningRead,
    NollningAddGroup,
    NollningDeleteMission,
    NollningGroupRead,
)
from database import DB_dependency
from db_models.nollning_model import Nollning_DB
from db_models.nollning_group_model import NollningGroup_DB
from group_mission_model import GroupMission_DB
from services.nollning_service import (
    add_g_to_nollning,
    create_nollning,
    edit_nollning,
    remove_nollning,
    delete_group_m,
    get_all_groups_in_nollning,
)
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


@nollning_router.post(
    "/add_group/{id}", dependencies=[Permission.require("manage", "Nollning")], response_model=NollningRead
)
def add_group_to_nollning(db: DB_dependency, id: int, data: NollningAddGroup):
    return add_g_to_nollning(db, id, data)


@nollning_router.get(
    "/",
    dependencies=[Permission.require("view", "Nollning")],
    response_model=list[NollningGroupRead],
)
def get_all_nollning_groups(db: DB_dependency, id: int):
    return get_all_groups_in_nollning(db, id)


@nollning_router.delete(
    "/delete_group_mission/{id}",
    dependencies=[Permission.require("manage", "Nollning")],
    response_model=NollningDeleteMission,
)
def delete_group_mission(db: DB_dependency, id: int, data: NollningDeleteMission):
    return delete_group_m(db, id, data)


@nollning_router.delete(
    "/remove_group/{nollning_group_id}",
    dependencies=[Permission.require("manage", "Nollning")],
    response_model=NollningGroupRead,
)
def remove_group_from_nollning(db: DB_dependency, nollning_group_id: int):
    nollning_group = db.query(NollningGroup_DB).filter_by(id=nollning_group_id).one_or_none()

    if not nollning_group:
        raise HTTPException(404, detail="Group not in nollning")

    completed_missions = db.query(GroupMission_DB).filter_by(nollning_group_id=nollning_group.id).all()

    if completed_missions:
        raise HTTPException(409, detail="Group has missions in nollning and therefore cannot be unlinked")

    db.delete(nollning_group)
    db.commit()

    return nollning_group
