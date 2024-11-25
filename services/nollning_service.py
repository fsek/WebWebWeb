from fastapi import HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from api_schemas.adventure_mission_schema import AdventureMissionCreate
from api_schemas.nollning_schema import NollningCreate
from db_models.adventure_mission_model import AdventureMission_DB
from db_models.album_model import Album_DB
from db_models.img_model import Img_DB
from db_models.nollning_model import Nollning_DB
from helpers.constants import MAX_NOLLNING_DESC, MAX_NOLLNING_NAME


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
