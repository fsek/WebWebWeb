from fastapi import HTTPException
from sqlalchemy.orm import Session
from api_schemas.adventure_mission_schema import AdventureMissionCreate
from db_models.adventure_mission_model import AdventureMission_DB
from db_models.nollning_model import Nollning_DB
from helpers.constants import MAX_ADVENTURE_MISSION_DESC, MAX_ADVENTURE_MISSION_NAME


def create_adventure_mission_(db: Session, data: AdventureMissionCreate):

    if len(data.title) > MAX_ADVENTURE_MISSION_NAME:
        raise HTTPException(400, detail="Title too long")

    if len(data.description) > MAX_ADVENTURE_MISSION_DESC:
        raise HTTPException(400, detail="Description too long")

    nollning = db.query(Nollning_DB).filter(Nollning_DB.id == data.nollning_id).one_or_none()

    if not nollning:
        raise HTTPException(404, detail="Nollning not found")

    if data.max_points < data.min_points:
        raise HTTPException(400, detail="Max points cannot be lower than min points")

    if data.max_points < 1:
        raise HTTPException(400, detail="Max points has to be atleast 1")

    if data.min_points < 1:
        raise HTTPException(400, detail="Min points has to be atleast 1")

    new_adventure_mission = AdventureMission_DB(
        nollning_id=data.nollning_id,
        nollning_week=data.nollning_week,
        title=data.title,
        description=data.description,
        max_points=data.max_points,
        min_points=data.min_points,
    )

    db.add(new_adventure_mission)
    db.commit()

    return new_adventure_mission


def find_adventure_mission(db: Session, id: int):

    adventure_mission = db.query(AdventureMission_DB).filter(AdventureMission_DB.id == id).one_or_none()

    if adventure_mission is None:
        raise HTTPException(404, detail="Mission not found")

    return adventure_mission


def remove_adventure_mission(db: Session, id: int):

    adventure_mission = db.query(AdventureMission_DB).filter(AdventureMission_DB.id == id).one_or_none()

    if adventure_mission is None:
        raise HTTPException(404, detail="Mission not found")

    db.delete(adventure_mission)
    db.commit()

    return adventure_mission


def find_all_adventure_missions(db: Session, nollning_id: int):

    adventure_missions = db.query(AdventureMission_DB).filter(AdventureMission_DB.nollning_id == nollning_id)

    return adventure_missions


def edit_adventure_mission_(db: Session, id: int, data: AdventureMissionCreate):

    adventure_mission = db.query(AdventureMission_DB).filter(AdventureMission_DB.id == id).one_or_none()

    if not adventure_mission:
        raise HTTPException(404, detail="Mission not found")

    for var, value in vars(data).items():
        setattr(adventure_mission, var, value) if value else None

    db.commit()
    db.refresh(adventure_mission)

    return adventure_mission
