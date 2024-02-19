from fastapi import APIRouter
from database import DB_dependency

# TODO Fix album router and ablum schema

album_router = APIRouter()


@album_router.post("/")
def add_album(db: DB_dependency):
    return
