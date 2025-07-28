from fastapi import APIRouter, HTTPException
from api_schemas.group_mission_schema import GroupMissionCreate, GroupMissionRead, GroupMissionEdit
from api_schemas.nollning_schema import NollningDeleteMission
from database import DB_dependency
from db_models.adventure_mission_model import AdventureMission_DB
from db_models.group_mission_model import GroupMission_DB
from db_models.nollning_group_model import NollningGroup_DB
from services.nollning_service import delete_group_m
from user.permission import Permission
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from fastapi import APIRouter, HTTPException
from database import DB_dependency
from db_models.user_model import User_DB
from user.permission import Permission


group_mission_router = APIRouter()


@group_mission_router.post(
    "/{nollning_group_id}", dependencies=[Permission.require("view", "Nollning")], response_model=GroupMissionRead
)
def add_group_mission(
    db: DB_dependency,
    data: GroupMissionCreate,
    nollning_group_id: int,
    me: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Nollning")],
):
    nollning_group = db.query(NollningGroup_DB).filter(NollningGroup_DB.id == nollning_group_id).one_or_none()

    if not nollning_group:
        raise HTTPException(404, detail="Nollning group not found")

    nollning_group_user_ids = [user.id for user in nollning_group.group.users]

    if (not me.id in nollning_group_user_ids) and (not manage_permission):
        raise HTTPException(403, detail="You cannot register a mission for a group you are not in")

    adventure_mission = (
        db.query(AdventureMission_DB).filter(AdventureMission_DB.id == data.adventure_mission_id).one_or_none()
    )

    if not adventure_mission:
        raise HTTPException(404, detail="Adventure mission not found")

    if not adventure_mission.nollning_id == nollning_group.nollning_id:
        raise HTTPException(400, detail="Adventure mission not in given nollning")

    mission = (
        db.query(GroupMission_DB)
        .filter(GroupMission_DB.nollning_group_id == nollning_group.id)
        .filter(GroupMission_DB.adventure_mission_id == adventure_mission.id)
        .one_or_none()
    )

    if mission:
        raise HTTPException(400, detail="Group has already made an attempt for this mission")

    if (data.points > adventure_mission.max_points) or (data.points < adventure_mission.min_points):
        raise HTTPException(400, detail="Point input doesn't match adventure mission points")

    mission_group = GroupMission_DB(
        points=data.points,
        adventure_mission_id=data.adventure_mission_id,
        nollning_group_id=nollning_group_id,
    )

    try:
        db.add(mission_group)
        db.commit()

    except IntegrityError as _:
        db.rollback()

        raise HTTPException(400, detail="Group has already completed mission")

    return mission_group


@group_mission_router.patch(
    "/{nollning_group_id}", dependencies=[Permission.require("manage", "Nollning")], response_model=GroupMissionRead
)
def edit_group_mission(db: DB_dependency, data: GroupMissionEdit, nollning_group_id: int):
    nollning_group = db.query(NollningGroup_DB).filter(NollningGroup_DB.id == nollning_group_id).one_or_none()

    if not nollning_group:
        raise HTTPException(404, detail="Nollning group not found")

    adventure_mission = (
        db.query(AdventureMission_DB).filter(AdventureMission_DB.id == data.adventure_mission_id).one_or_none()
    )

    if not adventure_mission:
        raise HTTPException(404, detail="Adventure mission not found")

    if not adventure_mission.nollning_id == nollning_group.nollning_id:
        raise HTTPException(400, detail="Adventure mission not in given nollning")

    mission = (
        db.query(GroupMission_DB)
        .filter(GroupMission_DB.nollning_group_id == nollning_group.id)
        .filter(GroupMission_DB.adventure_mission_id == adventure_mission.id)
        .one_or_none()
    )

    if not mission:
        raise HTTPException(404, detail="Group mission not found")

    for var, value in vars(data).items():
        setattr(mission, var, value) if value is not None else None

    db.commit()
    db.refresh(mission)

    return mission


@group_mission_router.delete(
    "/{nollning_id}",
    dependencies=[Permission.require("manage", "Nollning")],
    status_code=204,
)
def remove_group_mission(db: DB_dependency, nollning_id: int, data: NollningDeleteMission):
    delete_group_m(db, nollning_id, data)


@group_mission_router.get(
    "/{nollning_group_id}", dependencies=[Permission.require("view", "Nollning")], response_model=list[GroupMissionRead]
)
def get_group_missions_from_nollning_group(db: DB_dependency, nollning_group_id: int):
    return db.query(GroupMission_DB).filter(GroupMission_DB.nollning_group_id == nollning_group_id).all()
