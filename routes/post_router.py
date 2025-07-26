import os
from pathlib import Path
from fastapi import APIRouter, File, Response, UploadFile
from fastapi.responses import FileResponse
from database import DB_dependency
from db_models.council_model import Council_DB
from db_models.post_model import Post_DB
from api_schemas.post_schemas import PostRead, PostCreate, PostUpdate
from helpers.image_checker import validate_image
from helpers.types import ALLOWED_EXT, ASSETS_BASE_PATH
from user.permission import Permission
from fastapi import status, HTTPException
from api_schemas.user_schemas import SimpleUserRead

post_router = APIRouter()


@post_router.get("/", response_model=list[PostRead])
def get_all_posts(db: DB_dependency):
    posts = db.query(Post_DB).all()
    return posts


@post_router.post("/", dependencies=[Permission.require("manage", "Post")], response_model=PostRead)
def create_post(data: PostCreate, db: DB_dependency):
    council = db.query(Council_DB).filter_by(id=data.council_id).one_or_none()
    if council is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    post = Post_DB(
        name_sv=data.name_sv,
        name_en=data.name_en,
        council_id=data.council_id,
        email=data.email,
        description_sv=data.description_sv,
        description_en=data.description_en,
    )
    db.add(post)
    db.commit()
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


@post_router.patch("/{post_id}", dependencies=[Permission.require("manage", "Post")], response_model=PostRead)
def update_post(post_id: int, updated_post: PostUpdate, db: DB_dependency):
    post = db.query(Post_DB).filter_by(id=post_id).one_or_none()
    if post is None:
        raise HTTPException(404, "Post not found")
    for var, value in vars(updated_post).items():
        setattr(post, var, value) if value else None
    db.commit()
    db.refresh(post)
    return post


@post_router.get("/{post_id}", dependencies=[Permission.require("manage", "Post")], response_model=PostRead)
def get_post(post_id: int, db: DB_dependency):
    post = db.query(Post_DB).filter(Post_DB.id == post_id).one_or_none()
    return post


@post_router.get("/users/{post_id}", response_model=list[SimpleUserRead])
def get_all_users_with_post(post_id: int, db: DB_dependency):
    posts = db.query(Post_DB).filter_by(id=post_id).one_or_none()
    if posts is None:
        raise HTTPException(404, detail="Post not found")
    return posts.users


@post_router.post("/{post_id}/image", dependencies=[Permission.require("manage", "Post")])
async def post_post_image(post_id: int, db: DB_dependency, image: UploadFile = File()):
    post = db.query(Post_DB).get(post_id)
    if not post:
        raise HTTPException(404, "No event found")

    if image:

        await validate_image(image)
        filename: str = str(image.filename)
        _, ext = os.path.splitext(filename)

        ext = ext.lower()

        if ext not in ALLOWED_EXT:
            raise HTTPException(400, "file extension not allowed")

        dest_path = Path(f"{ASSETS_BASE_PATH}/posts/{post.id}")

        dest_path.write_bytes(image.file.read())


@post_router.get("/{post_id}/image", dependencies=[Permission.require("manage", "Post")])
def get_post_image(post_id: int, db: DB_dependency):
    post = db.query(Post_DB).get(post_id)
    if not post:
        raise HTTPException(404, "No image for this post")

    internal = f"/{ASSETS_BASE_PATH}/posts/{post.id}"

    return Response(status_code=200, headers={"X-Accel-Redirect": internal})


@post_router.get("/{post_id}/image/stream", dependencies=[Permission.require("manage", "Post")])
def get_post_image_stream(post_id: int, db: DB_dependency):
    post = db.query(Post_DB).get(post_id)
    if not post:
        raise HTTPException(404, "No image for this post")

    internal = f"/{ASSETS_BASE_PATH}/posts/{post.id}"

    return FileResponse(internal)
