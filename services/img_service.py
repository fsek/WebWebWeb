from fastapi import HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pathlib import Path
from db_models.img_model import Img_DB
import random


def upload_img(db: Session, file: UploadFile = File()):
    try:
        salt = random.getrandbits(24)

        # file_path = Path(f"/path_to_put/{str(hash)}.jpeg")

        if file.filename is None:
            raise HTTPException(400, detail="The file has no name")

        file_path = Path(f"/{salt}{file.filename.replace(' ', '')}")
        if file_path.is_file():
            raise HTTPException(409, detail="Filename is equal to already existing file")

        file_path.write_bytes(file.file.read())
        img = Img_DB(path=file_path.name)
        db.add(img)
        db.commit
        return {"message": "File saved successfully"}

    except Exception as e:
        raise e
