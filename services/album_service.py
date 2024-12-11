from fastapi import HTTPException
from sqlalchemy.orm import Session
from api_schemas.album_schema import AlbumCreate
from db_models.album_model import Album_DB
from pathlib import Path
import os


def add_album(db: Session, album: AlbumCreate):
    file_path = Path(f"/{album.name}")
    if file_path.is_dir() or file_path.is_file():
        raise HTTPException(409, detail="album or file with this name already exists")

    file_path.mkdir()
    new_album = Album_DB(name=album.name, path=file_path.name)
    db.add(new_album)
    db.commit()

    return {"message": "Album successfully created"}


def get_all_albums(db: Session):
    albums = db.query(Album_DB).all()
    return albums


def get_album(db: Session, id: int):
    album = db.query(Album_DB).filter(Album_DB.id == id).one_or_none()
    if album is None:
        raise HTTPException(404, detail="Album not found")

    return album


def delete_album(db: Session, id: int):
    album = db.query(Album_DB).filter(Album_DB.id == id).one_or_none()
    if album is None:
        raise HTTPException(404, detail="Album not found")

    if len(album.imgs) != 0:
        raise HTTPException(404, detail="Album isn't empty")

    os.rmdir(f"/{album.path}")
    db.delete(album)
    db.commit()

    return {"message": "Album removed successfully"}
