from fastapi import APIRouter
from database import DB_dependency
from db_models.post_model import Post_DB
from schemas.post_schemas import PostRead

post_router = APIRouter()


@post_router.get("/", response_model=list[PostRead])
def get_all_posts(db: DB_dependency):
    posts = db.query(Post_DB).all()
    return posts


# TODO POST

# TODO DELETE

# TODO PATCH
