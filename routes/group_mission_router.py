from fastapi import APIRouter, HTTPException
from api_schemas.group_schema import GroupAddUser, GroupCreate, GroupRead, GroupRemoveUser
from api_schemas.group_mission_schema import GroupMissionCreate
from database import DB_dependency
from db_models.adventure_mission_model import AdventureMission_DB
from db_models.group_mission_model import GroupMission_DB
from db_models.nollning_group_model import NollningGroup_DB
from db_models.nollning_model import Nollning_DB
from user.permission import Permission


group_mission_router = APIRouter()


@group_mission_router.post(
    "/", dependencies=[Permission.require("manage", "Nollning")], response_model=GroupMissionCreate
)
def add_completed_mission(db: DB_dependency, data: GroupMissionCreate):
    nollning_group = db.query(NollningGroup_DB).filter(NollningGroup_DB.id == data.nollning_group_id).one_or_none()

    if not nollning_group:
        raise HTTPException(404, detail="Nollning group not found")

    adventure_mission = (
        db.query(AdventureMission_DB).filter(AdventureMission_DB.id == data.adventure_mission_id).one_or_none()
    )

    if not adventure_mission:
        raise HTTPException(404, detail="Adventure mission not found")

    mission_group = GroupMission_DB(
        points=data.points,
        adventure_mission_id=data.adventure_mission_id,
        adventure_mission=adventure_mission,
        nollning_group_id=data.nollning_group_id,
        nollning_group=nollning_group,
    )

    db.add(mission_group)
    db.commit()

    return mission_group


@group_mission_router.get(
    "/{id}", dependencies=[Permission.require("manage", "Nollning")], response_model=list[GroupMissionCreate]
)
def get_completed_missions(db: DB_dependency, id: int):

    completed = db.query(GroupMission_DB).join(NollningGroup_DB, NollningGroup_DB.id == GroupMission_DB.nollning_group_id).join(Nollning_DB, Nollning_DB.id == NollningGroup_DB.nollning_id).filter(Nollning_DB.id == id).all()
    
    # completed = db.query(Nollning_DB).join(NollningGroup_DB).join(GroupMission_DB).filter(Nollning_DB.id == id).all()
    

    return completed
