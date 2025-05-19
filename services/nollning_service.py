from fastapi import HTTPException
from sqlalchemy.orm import Session
from api_schemas.nollning_schema import NollningAddGroup, NollningCreate, NollningDeleteMission
from db_models.group_model import Group_DB
from db_models.nollning_group_model import NollningGroup_DB
from db_models.nollning_model import Nollning_DB
from db_models.group_mission_model import GroupMission_DB


def create_nollning(db: Session, data: NollningCreate):
    nollning = Nollning_DB(name=data.name, description=data.description)

    db.add(nollning)
    db.commit()

    return nollning


def edit_nollning(db: Session, id: int, data: NollningCreate):
    nollning = db.query(Nollning_DB).filter(Nollning_DB.id == id).one_or_none()

    if not nollning:
        raise HTTPException(404, detail="Nollning not found")

    for var, value in vars(data).items():
        setattr(nollning, var, value) if value else None

    db.commit()
    db.refresh(nollning)

    return nollning


def remove_nollning(db: Session, id: int):
    nollning = db.query(Nollning_DB).filter(Nollning_DB.id == id).one_or_none()

    if not nollning:
        raise HTTPException(404, detail="Nollning not found")

    db.delete(nollning)
    db.commit()

    return {"message": "Nollning removed successfully"}


def add_g_to_nollning(db: Session, id: int, data: NollningAddGroup):
    nollning = db.query(Nollning_DB).filter(Nollning_DB.id == id).one_or_none()

    if not nollning:
        raise HTTPException(404, detail="Nollning not found")

    group = db.query(Group_DB).filter(Group_DB.id == data.group_id).one_or_none()

    if group == None:
        raise HTTPException(404, detail="Group not found")

    for nollning_group in nollning.nollning_groups:
        if nollning_group.group_id == data.group_id:
            raise HTTPException(400, detail="Group already in nollning")

    nollning_group = NollningGroup_DB(group=group, group_id=group.id, nollning=nollning, nollning_id=nollning.id)

    db.add(nollning_group)
    db.commit()
    db.refresh(nollning)

    return nollning


def get_all_groups_in_nollning(db: Session, id: int):
    nollning = db.query(Nollning_DB).filter(Nollning_DB.id == id).one_or_none()

    if not nollning:
        raise HTTPException(404, detail=f"No nollning found")

    if not nollning.nollning_groups:
        raise HTTPException(404, detail=f"No groups found")

    return nollning.nollning_groups


def delete_group_m(db: Session, id: int, data: NollningDeleteMission):
    adventure_mission = (
        db.query(GroupMission_DB)
        .filter(
            GroupMission_DB.nollning_group_id == data.group_id, GroupMission_DB.adventure_mission_id == data.mission_id
        )
        .one_or_none()
    )

    if not adventure_mission:
        raise HTTPException(404, detail=f"Adventure mission or group not found")

    db.delete(adventure_mission)
    db.commit()

    return adventure_mission
