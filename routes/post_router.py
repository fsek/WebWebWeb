from fastapi import APIRouter
from database import DB_dependency
from db_models.post_model import Post_DB, PostUser_DB
from api_schemas.post_schemas import PostRead
from fastapi import status, HTTPException
from user.permission import Permission


post_router = APIRouter()


@post_router.get("/", response_model=list[PostRead])
def get_all_posts(db: DB_dependency):
    posts = db.query(Post_DB).all()
    return posts


# TODO POST


@post_router.delete(
    "/{post_id}", dependencies=[Permission.require("manage", "Post")], status_code=status.HTTP_204_NO_CONTENT
)
def delete_post(post_id: int, db: DB_dependency):
    post = db.query(Post_DB).filter_by(id=post_id).one_or_none()
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    db.delete(post)
    peopleWithPost = db.query(PostUser_DB).filter_by(id=post_id)
    db.delete(peopleWithPost)
    db.commit()
    return status.HTTP_204_NO_CONTENT


# TODO PATCH
