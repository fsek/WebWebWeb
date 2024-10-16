from fastapi import HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from api_schemas.adventure_mission_schema import AdventureMissionCreate
from db_models.adventure_mission_model import AdventureMission_DB
from db_models.album_model import Album_DB
from db_models.img_model import Img_DB
from helpers.constants import MAX_ADVENTURE_MISSION_DESC, MAX_ADVENTURE_MISSION_NAME


def create_adventure_mission(db: Session, data: AdventureMissionCreate):

    if len(data.title) > MAX_ADVENTURE_MISSION_NAME:
        raise HTTPException(400, detail="Title too long")

    if len(data.description) > MAX_ADVENTURE_MISSION_DESC:
        raise HTTPException(400, detail="Description too long")

    new_adventure_mission = AdventureMission_DB(
        nollning_week=data.nollning_week, title=data.title, description=data.description, points=data.points
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

    return {"message": "File removed successfully"}


def find_all_adventure_missions(db: Session):

    adventure_missions = db.query(AdventureMission_DB).all()

    return adventure_missions
