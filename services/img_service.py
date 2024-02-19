from datetime import UTC, datetime
from annotated_types import LowerCase
from fastapi import HTTPException, status, UploadFile, File
from pydantic import FilePath
from sqlalchemy.orm import Session
from PIL import Image
from fastapi.responses import FileResponse
import os.path
from pathlib import Path
from db_models.img_model import Img_DB
import random


def upload_img(db: Session, file: UploadFile = File()):
    # This will be moved to services later
    try:
        hash = random.getrandbits(128)

        file_path = Path(f"/path_to_put/{str(hash)}.jpeg")
        # file_path = Path(f"/path_to_put/1.png") {str(Image.open(file.file).format).lower()}")
        if file_path.is_file():
            raise HTTPException(409)

        file_path.write_bytes(file.file.read())
        img = Img_DB(path=file_path.name)
        db.add(img)
        db.commit
        return {"message": "File saved successfully"}

    except Exception as e:
        raise e
