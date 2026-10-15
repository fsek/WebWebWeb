from fastapi import HTTPException
from sqlalchemy.orm import Session
from api_schemas.adventure_mission_schema import AdventureMissionCreate
from db_models.adventure_mission_model import AdventureMission_DB
from db_models.nollning_model import Nollning_DB
from helpers.constants import (
    MAX_ADVENTURE_MISSION_DESC,
    MAX_ADVENTURE_MISSION_NAME,
    MAX_ADVENTURE_MISSION_UNLOCK_HINT,
    MAX_ADVENTURE_MISSION_UNLOCK_CODE,
)


def create_adventure_mission_(db: Session, data: AdventureMissionCreate, nollning_id: int):

    if len(data.title_sv) > MAX_ADVENTURE_MISSION_NAME or len(data.title_en) > MAX_ADVENTURE_MISSION_NAME:
        raise HTTPException(400, detail="Title too long")

    if len(data.description_sv) > MAX_ADVENTURE_MISSION_DESC or len(data.description_en) > MAX_ADVENTURE_MISSION_DESC:
        raise HTTPException(400, detail="Description too long")

    if (
        len(data.unlock_hint_sv or "") > MAX_ADVENTURE_MISSION_UNLOCK_HINT
        or len(data.unlock_hint_en or "") > MAX_ADVENTURE_MISSION_UNLOCK_HINT
    ):
        raise HTTPException(400, detail="Unlock hint too long")

    if len(data.unlock_code or "") > MAX_ADVENTURE_MISSION_UNLOCK_CODE:
        raise HTTPException(400, detail="Unlock code too long")

    nollning = db.query(Nollning_DB).filter(Nollning_DB.id == nollning_id).one_or_none()

    if not nollning:
        raise HTTPException(404, detail="Nollning not found")

    if data.max_points < data.min_points:
        raise HTTPException(400, detail="Max points cannot be lower than min points")

    if data.max_points < 1:
        raise HTTPException(400, detail="Max points has to be atleast 1")

    if data.min_points < 0:
        raise HTTPException(400, detail="Min points has to be atleast 0")

    if data.unlock_code == "":  # Easy guard against accidentally setting unlock_code to empty string
        data.unlock_code = None
    if data.unlock_hint_sv == "":
        data.unlock_hint_sv = None
    if data.unlock_hint_en == "":
        data.unlock_hint_en = None

    new_adventure_mission = AdventureMission_DB(
        nollning_id=nollning_id,
        nollning_week=data.nollning_week,
        title_sv=data.title_sv,
        title_en=data.title_en,
        description_sv=data.description_sv,
        description_en=data.description_en,
        max_points=data.max_points,
        min_points=data.min_points,
        mission_category=data.mission_category if data.mission_category is not None else "Spel",
        unlock_code=data.unlock_code,
        unlock_hint_sv=data.unlock_hint_sv,
        unlock_hint_en=data.unlock_hint_en,
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

    adventure_missions = db.query(AdventureMission_DB).filter(AdventureMission_DB.nollning_id == nollning_id).all()

    return adventure_missions


def edit_adventure_mission_(db: Session, id: int, data: AdventureMissionCreate):

    adventure_mission = db.query(AdventureMission_DB).filter(AdventureMission_DB.id == id).one_or_none()

    if len(data.title_sv) > MAX_ADVENTURE_MISSION_NAME or len(data.title_en) > MAX_ADVENTURE_MISSION_NAME:
        raise HTTPException(400, detail="Title too long")

    if len(data.description_sv) > MAX_ADVENTURE_MISSION_DESC or len(data.description_en) > MAX_ADVENTURE_MISSION_DESC:
        raise HTTPException(400, detail="Description too long")

    if (
        len(data.unlock_hint_sv or "") > MAX_ADVENTURE_MISSION_UNLOCK_HINT
        or len(data.unlock_hint_en or "") > MAX_ADVENTURE_MISSION_UNLOCK_HINT
    ):
        raise HTTPException(400, detail="Unlock hint too long")

    if len(data.unlock_code or "") > MAX_ADVENTURE_MISSION_UNLOCK_CODE:
        raise HTTPException(400, detail="Unlock code too long")

    if not adventure_mission:
        raise HTTPException(404, detail="Mission not found")

    if data.max_points < data.min_points:
        raise HTTPException(400, detail="Max points cannot be lower than min points")

    if data.max_points < 1:
        raise HTTPException(400, detail="Max points has to be atleast 1")

    if data.min_points < 0:
        raise HTTPException(400, detail="Min points has to be atleast 0")

    if data.unlock_code == "":  # Easy guard against accidentally setting unlock_code to empty string
        data.unlock_code = None
    if data.unlock_hint_sv == "":
        data.unlock_hint_sv = None
    if data.unlock_hint_en == "":
        data.unlock_hint_en = None

    if data.mission_category is None:
        data.mission_category = "Spel"

    for var, value in vars(data).items():
        # Allow for clearing of unlock_code by allowing setting attributes to None
        setattr(adventure_mission, var, value)

    db.commit()
    db.refresh(adventure_mission)

    return adventure_mission
