from fastapi import APIRouter, HTTPException
from api_schemas.group_mission_schema import (
    GroupMissionCreate,
    GroupMissionRead,
    GroupMissionEdit,
    GroupMissionDelete,
)
from database import DB_dependency
from db_models.adventure_mission_model import AdventureMission_DB
from db_models.group_mission_model import GroupMission_DB
from db_models.nollning_group_model import NollningGroup_DB
from user.permission import Permission
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from fastapi import APIRouter, HTTPException
from database import DB_dependency
from db_models.user_model import User_DB
from user.permission import Permission


group_mission_router = APIRouter()


@group_mission_router.post("/{nollning_group_id}", dependencies=[Permission.member()], response_model=GroupMissionRead)
def add_group_mission(
    db: DB_dependency,
    data: GroupMissionCreate,
    nollning_group_id: int,
    me: Annotated[User_DB, Permission.member()],
    manage_permission: Annotated[bool, Permission.check("manage", "Nollning")],
):
    # A route to add a completed mission for a group in a nollning
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

    attempted_mission = (
        db.query(GroupMission_DB)
        .filter(GroupMission_DB.nollning_group_id == nollning_group.id)
        .filter(GroupMission_DB.adventure_mission_id == adventure_mission.id)
        .one_or_none()
    )

    if attempted_mission:
        raise HTTPException(400, detail="Group has already made an attempt for this mission")

    if not manage_permission:
        data.points = None
        data.is_accepted = None

    mission_group = GroupMission_DB(
        points=data.points if data.points is not None else adventure_mission.min_points,
        adventure_mission_id=data.adventure_mission_id,
        nollning_group_id=nollning_group_id,
        is_accepted=data.is_accepted if data.is_accepted is not None else "Review",
    )

    try:
        db.add(mission_group)
        db.commit()

    except IntegrityError as _:
        db.rollback()

        raise HTTPException(400, detail="Group has already attempted mission, edit the attempt instead")

    return mission_group


@group_mission_router.patch(
    "/{nollning_group_id}", dependencies=[Permission.require("manage", "Nollning")], response_model=GroupMissionRead
)
def edit_group_mission(db: DB_dependency, data: GroupMissionEdit, nollning_group_id: int):
    # A route to edit a completed mission for a group in a nollning
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

    attempted_mission = (
        db.query(GroupMission_DB)
        .filter(GroupMission_DB.nollning_group_id == nollning_group.id)
        .filter(GroupMission_DB.adventure_mission_id == adventure_mission.id)
        .one_or_none()
    )

    if not attempted_mission:
        raise HTTPException(404, detail="Group has not attempted this mission")

    for var, value in vars(data).items():
        setattr(attempted_mission, var, value) if value is not None else None

    db.commit()
    db.refresh(attempted_mission)

    return attempted_mission


@group_mission_router.delete(
    "/{nollning_group_id}", dependencies=[Permission.require("manage", "Nollning")], response_model=GroupMissionRead
)
def delete_group_mission(db: DB_dependency, data: GroupMissionDelete, nollning_group_id: int):
    # A route to delete a completed mission (i.e., uncomplete) for a group in a nollning

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

    attempted_mission = (
        db.query(GroupMission_DB)
        .filter(GroupMission_DB.nollning_group_id == nollning_group.id)
        .filter(GroupMission_DB.adventure_mission_id == adventure_mission.id)
        .one_or_none()
    )

    if not attempted_mission:
        raise HTTPException(404, detail="Group has not attempted this mission")

    # Delete the mission
    db.delete(attempted_mission)
    db.commit()

    return attempted_mission


@group_mission_router.get(
    "/{nollning_group_id}", dependencies=[Permission.require("view", "Nollning")], response_model=list[GroupMissionRead]
)
def get_group_missions_from_nollning_group(db: DB_dependency, nollning_group_id: int):
    return db.query(GroupMission_DB).filter(GroupMission_DB.nollning_group_id == nollning_group_id).all()
