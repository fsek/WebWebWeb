from fastapi import APIRouter
from database import DB_dependency
from db_models.council_model import Council_DB
from db_models.post_model import Post_DB
from api_schemas.post_schemas import PostRead, PostCreate
from services.post_service import create_new_post
from user.permission import Permission
from fastapi import status, HTTPException

post_router = APIRouter()


@post_router.get("/", response_model=list[PostRead])
def get_all_posts(db: DB_dependency):
    posts = db.query(Post_DB).all()
    return posts


@post_router.post("/", dependencies=[Permission.require("manage", "Post")], response_model=PostRead)
def create_post(data: PostCreate, db: DB_dependency):
    council = db.query(Council_DB).filter_by(council_id=data.council_id).one_or_none()
    if council is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    post = create_new_post(data, db)
    return post


@post_router.delete(
    "/{post_id}", dependencies=[Permission.require("manage", "Post")], status_code=status.HTTP_204_NO_CONTENT
)
def delete_post(post_id: int, db: DB_dependency):
    post = db.query(Post_DB).filter_by(id=post_id).one_or_none()
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    db.delete(post)
    db.commit()
    return


# TODO PATCH
