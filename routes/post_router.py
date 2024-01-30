from fastapi import APIRouter
from database import DB_dependency
from db_models.post_model import Post_DB
from api_schemas.post_schemas import PostRead, PostCreate
from user.permission import Permission
from services.post_service import *

post_router = APIRouter()


@post_router.get("/", response_model=list[PostRead])
def get_all_posts(db: DB_dependency):
    posts = db.query(Post_DB).all()
    return posts


# TODO POST


@post_router.post("/", dependencies=[Permission.require("manage", "Post")], response_model=PostRead)
def create_post(data: PostCreate, db: DB_dependency):
    post = create_new_post(data, db)
    return post


# TODO DELETE

# TODO PATCH
