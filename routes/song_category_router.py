from database import DB_dependency
from api_schemas.song_category_schemas import SongCategoryCreate, SongCategoryRead
from db_models.song_category_model import SongCategory_DB
from fastapi import APIRouter, HTTPException, status
from user.permission import Permission


song_category_router = APIRouter()


@song_category_router.get("/", response_model=list[SongCategoryRead])
def get_all_song_categories(db: DB_dependency):
    categories = db.query(SongCategory_DB).all()
    return categories


@song_category_router.get("/{category_id}", response_model=SongCategoryRead)
def get_song_category(category_id: int, db: DB_dependency):
    category = db.query(SongCategory_DB).filter_by(id=category_id).one_or_none()
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return category


@song_category_router.post("/", response_model=SongCategoryRead, dependencies=[Permission.require("manage", "Song")])
def create_song_category(song_category_data: SongCategoryCreate, db: DB_dependency):
    num_existing = db.query(SongCategory_DB).filter(SongCategory_DB.name == song_category_data.name).count()
    if num_existing > 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Ths post already exists")
    songcategory = SongCategory_DB(name=song_category_data.name)
    db.add(songcategory)
    db.commit()
    return songcategory


@song_category_router.delete(
    "/{category_id}", response_model=SongCategoryRead, dependencies=[Permission.require("manage", "Song")]
)
def delete_song_category(category_id: int, db: DB_dependency):
    category = db.query(SongCategory_DB).filter_by(id=category_id).one_or_none()
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    # Moves songs belonging to deleted category to default category
    for song in category.songs:
        song.category_id = None

    db.delete(category)
    db.commit()
    return category


@song_category_router.patch(
    "/{category_id}", response_model=SongCategoryRead, dependencies=[Permission.require("manage", "Song")]
)
def update_song_category(category_id: int, category_data: SongCategoryCreate, db: DB_dependency):
    category = db.query(SongCategory_DB).filter_by(id=category_id).one_or_none()
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    category.name = category_data.name
    db.commit()
    return category
