from fastapi import HTTPException
from sqlalchemy.orm import Session
from api_schemas.album_schema import AlbumCreate
from db_models.album_model import Album_DB
from pathlib import Path
import os
import re
from helpers.db_util import sanitize_title


from db_models.user_model import User_DB


base_path = os.getenv("ALBUM_BASE_PATH")


def add_album(db: Session, album: AlbumCreate):

    file_path = Path(f"{base_path}/{album.year}/{sanitize_title(album.title_sv)}")

    if not Path(f"{base_path}/{album.year}").exists():
        os.mkdir(f"{base_path}/{album.year}")

    if file_path.is_dir() or file_path.is_file():
        raise HTTPException(409, detail="album or file already exists")

    file_path.mkdir()
    new_album = Album_DB(
        title_en=album.title_en,
        title_sv=album.title_sv,
        desc_en=album.desc_en,
        desc_sv=album.desc_sv,
        path=str(file_path.resolve()),
        year=album.year,
        location=album.location,
        date=album.date,
    )
    db.add(new_album)
    db.commit()

    return new_album


def add_photographer(db: Session, album_id: int, user_id: int):
    album = db.query(Album_DB).filter(Album_DB.id == album_id).one_or_none()

    if not album:
        raise HTTPException(404, detail="Album not found")

    user = db.query(User_DB).filter(User_DB.id == user_id).one_or_none()

    if not user:
        raise HTTPException(404, detail="User not found")

    album.photographer_id = user_id

    db.commit()

    return album


def get_all_albums(db: Session):
    albums = db.query(Album_DB).all()
    return albums


def get_album(db: Session, album_id: int):
    album = db.query(Album_DB).filter(Album_DB.id == album_id).one_or_none()
    if album is None:
        raise HTTPException(404, detail="Album not found")

    return album


def delete_album(db: Session, id: int):
    album = db.query(Album_DB).filter(Album_DB.id == id).one_or_none()
    if album is None:
        raise HTTPException(404, detail="Album not found")

    if len(album.imgs) != 0:
        raise HTTPException(404, detail="Album isn't empty")

    os.rmdir(f"{album.path}")
    db.delete(album)
    db.commit()

    return album


def delete_year(db: Session, year: int):
    path = Path(f"{base_path}/{year}")
    if not path.exists():
        raise HTTPException(404, detail="Year not in database")

    if any(path.iterdir()):
        raise HTTPException(409, detail="Year directory has other files/directories")

    os.rmdir(path)

    return {"message": "Year successfully deleted"}
