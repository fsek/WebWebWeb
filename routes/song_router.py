from fastapi import APIRouter, HTTPException, status
from api_schemas.song_schemas import SongCreate, SongRead
from database import DB_dependency
from db_models.song_model import Song_DB
from user.permission import Permission


song_router = APIRouter()


@song_router.get("/", response_model=list[SongRead])
def get_all_songs(db: DB_dependency):
    songs = db.query(Song_DB).all()
    return songs


@song_router.get("/{song_id}", response_model=SongRead)
def get_song(song_id: int, db: DB_dependency):
    song = db.query(Song_DB).filter_by(id=song_id).one_or_none()

    if song is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    song.views += 1
    db.commit()

    return song


@song_router.post("/", response_model=SongRead, dependencies=[Permission.require("manage", "Song")])
def create_song(song_data: SongCreate, db: DB_dependency):
    num_existing = db.query(Song_DB).filter(Song_DB.title == song_data.title).count()
    if num_existing > 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Ths post already exists")
    song = Song_DB(
        title=song_data.title,
        author=song_data.author,
        content=song_data.content,
        category_id=song_data.category_id,
        melody=song_data.melody,
    )
    db.add(song)
    db.commit()
    return song


@song_router.delete("/{song_id}", response_model=SongRead, dependencies=[Permission.require("manage", "Song")])
def delete_song(song_id: int, db: DB_dependency):
    song = db.query(Song_DB).filter_by(id=song_id).one_or_none()
    if song is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    db.delete(song)
    db.commit()
    return song


@song_router.patch("/{song_id}", response_model=SongRead, dependencies=[Permission.require("manage", "Song")])
def update_song(song_id: int, song_data: SongCreate, db: DB_dependency):
    song = db.query(Song_DB).filter_by(id=song_id).one_or_none()
    if song is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    # This does not allow one to "unset" values that could be null but aren't currently
    for var, value in vars(song_data).items():
        setattr(song, var, value) if value else None

    db.commit()
    return song
