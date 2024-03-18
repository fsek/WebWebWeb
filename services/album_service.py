from fastapi import HTTPException
from sqlalchemy.orm import Session
from api_schemas.album_schema import AlbumCreate
from db_models.album_model import Album_DB

def add_album(db: Session, album: AlbumCreate):
    new_album = Album_DB(name=album.name)
    db.add(new_album)
    db.commit()

    return {"message": "Album successfully created"}


def get_all_albums(db: Session):
    albums = db.query(Album_DB).all()
    return albums


def get_album(db: Session, id: int):
    try:
        album = db.query(Album_DB).filter(Album_DB.id == id).one_or_none()
        if album is None:
            raise HTTPException(404, detail="Album not found")

        return album

    except Exception as e:
        raise e