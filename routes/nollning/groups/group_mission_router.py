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


group_mission_router = APIRouter()


@group_mission_router.post(
    "/{mission_id}", dependencies=[Permission.require("manage", "Nollning")], response_model=GroupMissionRead
)
def add_completed_mission_to_group(db: DB_dependency, data: GroupMissionCreate, group_id: int):
    nollning_group = db.query(NollningGroup_DB).filter(NollningGroup_DB.id == group_id).one_or_none()

    if not nollning_group:
        raise HTTPException(404, detail="Nollning group not found")

    adventure_mission = (
        db.query(AdventureMission_DB).filter(AdventureMission_DB.id == data.adventure_mission_id).one_or_none()
    )

    if not adventure_mission:
        raise HTTPException(404, detail="Adventure mission not found")

    if not adventure_mission.nollning_id == nollning_group.nollning_id:
        raise HTTPException(400, detail="Adventure mission not in given nollning")

    mission_group = GroupMission_DB(
        points=data.points,
        adventure_mission_id=data.adventure_mission_id,
        adventure_mission=adventure_mission,
        nollning_group_id=group_id,
        nollning_group=nollning_group,
    )

    try:
        db.add(mission_group)
        db.commit()

    except IntegrityError as e:
        db.rollback()

        raise HTTPException(400, detail="Group has already completed mission")

    return mission_group


@group_mission_router.patch(
    "/{mission_id}", dependencies=[Permission.require("manage", "Nollning")], response_model=GroupMissionRead
)
def edit_completed_mission_in_group(db: DB_dependency, data: GroupMissionEdit, group_id: int):
    nollning_group = db.query(NollningGroup_DB).filter(NollningGroup_DB.id == group_id).one_or_none()

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
    "/{mission_id}",
    dependencies=[Permission.require("manage", "Nollning")],
    status_code=204,
)
def remove_completed_mission_from_group(db: DB_dependency, nollning_id: int, data: NollningDeleteMission):
    delete_group_m(db, nollning_id, data)


@group_mission_router.get(
    "/", dependencies=[Permission.require("view", "Nollning")], response_model=list[GroupMissionRead]
)
def get_completed_missions_from_group(db: DB_dependency, nollning_id: int, group_id: int):
    return db.query(GroupMission_DB).filter(GroupMission_DB.nollning_group_id == group_id).all()
