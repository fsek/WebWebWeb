from fastapi import HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from db_models.associated_img_model import AssociatedImg_DB
from helpers.constants import MAX_IMG_NAME
from helpers.types import ASSOCIATION_TYPES
import random
import os
from helpers.db_util import sanitize_title
from sqlalchemy.exc import IntegrityError
from db_models.program_model import Program_DB
from db_models.program_year_model import ProgramYear_DB
from db_models.course_model import Course_DB
from db_models.specialisation_model import Specialisation_DB


def upload_img(
    db: Session,
    association_type: ASSOCIATION_TYPES,
    association_id: int,
    file: UploadFile = File(),
):
    base_path = os.getenv("ASSOCIATED_IMG_BASE_PATH")
    if base_path is None:
        raise HTTPException(500, detail="Server configuration error: ASSOCIATED_IMG_BASE_PATH not set")

    if file.filename is None:
        raise HTTPException(400, detail="The file has no name")

    if len(file.filename) > MAX_IMG_NAME:
        raise HTTPException(400, detail="The file name is too long")

    match association_type:
        case "program":
            association = db.query(Program_DB).filter(Program_DB.program_id == association_id).one_or_none()
        case "program_year":
            association = (
                db.query(ProgramYear_DB).filter(ProgramYear_DB.program_year_id == association_id).one_or_none()
            )
        case "course":
            association = db.query(Course_DB).filter(Course_DB.course_id == association_id).one_or_none()
        case "specialisation":
            association = (
                db.query(Specialisation_DB).filter(Specialisation_DB.specialisation_id == association_id).one_or_none()
            )
        case _:
            raise HTTPException(400, detail="Invalid association type")
    if association == None:
        raise HTTPException(404, detail="Associated entity for image not found")

    salt = random.getrandbits(24)

    name, ext = os.path.splitext(file.filename)

    sanitized_filename = sanitize_title(name)

    allowed_exts = {".png", ".jpg", ".jpeg", ".gif"}

    ext = ext.lower()

    if ext not in allowed_exts:
        raise HTTPException(400, "file extension not allowed")

    BASE_UPLOAD_DIR = Path(f"{base_path}")

    file.filename = sanitized_filename

    file_path = Path(f"{BASE_UPLOAD_DIR}/{salt}{sanitized_filename}{ext}")
    if file_path.is_file():
        raise HTTPException(409, detail="Filename is equal to already existing file")

    img = AssociatedImg_DB(path=str(file_path))
    association.associated_img = img

    try:
        db.add(img)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, detail="Invalid tag name")

    file_path.write_bytes(file.file.read())

    return {"message": "File saved successfully"}


def remove_img(db: Session, img_id: int):
    img = db.query(AssociatedImg_DB).filter(AssociatedImg_DB.associated_img_id == img_id).one_or_none()

    if img == None:
        raise HTTPException(404, detail="File not found")

    if img.program is not None:
        img.program.associated_img = None
    if img.program_year is not None:
        img.program_year.associated_img = None
    if img.course is not None:
        img.course.associated_img = None
    if img.specialisation is not None:
        img.specialisation.associated_img = None

    os.remove(img.path)
    db.delete(img)
    db.commit()

    return {"message": "File removed successfully"}


def get_single_img(db: Session, img_id: int):
    img = db.query(AssociatedImg_DB).filter(AssociatedImg_DB.associated_img_id == img_id).one_or_none()

    if img == None:
        raise HTTPException(404, detail="File not found")

    return FileResponse(img.path)
