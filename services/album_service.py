from fastapi import HTTPException
from sqlalchemy.orm import Session
from api_schemas.album_schema import AlbumCreate
from db_models.album_model import Album_DB
from pathlib import Path
import os


def normalize_swedish(text: str) -> str:
    replacements = {"å": "a", "ä": "a", "ö": "o", "Å": "A", "Ä": "A", "Ö": "O"}
    return "".join(replacements.get(c, c) for c in text)


def add_album(db: Session, album: AlbumCreate):
    file_path = Path(f"/albums/{album.year}/{normalize_swedish(album.name).lower().replace(' ', '')}")

    if not Path(f"/albums/{album.year}").exists():
        os.mkdir(f"/albums/{album.year}")

    if file_path.is_dir() or file_path.is_file():
        raise HTTPException(409, detail="album or file already exists")

    file_path.mkdir()
    new_album = Album_DB(name=album.name, path=str(file_path.resolve()), year=album.year)
    db.add(new_album)
    db.commit()

    return new_album


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
    path = Path(f"/albums/{year}")
    if not path.exists():
        raise HTTPException(404, detail="Year not in database")

    if any(path.iterdir()):
        raise HTTPException(409, detail="Year directory has other files/directories")

    os.rmdir(path)

    return {"message": "Year successfully deleted"}
