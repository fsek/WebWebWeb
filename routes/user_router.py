import os
from pathlib import Path
from typing import Annotated, Optional
from fastapi.responses import FileResponse
from sqlalchemy import ColumnElement, and_, or_
from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from database import DB_dependency
from db_models.user_model import User_DB
from api_schemas.user_schemas import (
    AdminUserRead,
    UpdateUserMember,
    UpdateUserMemberMultiple,
    UserUpdate,
    UserRead,
    UpdateUserPosts,
)
from user.user_stuff import USERS
from fastapi_users_pelicanq.manager import BaseUserManager
from helpers.image_checker import validate_image
from helpers.rate_limit import rate_limit
from helpers.types import ALLOWED_EXT, ALLOWED_IMG_SIZES, ALLOWED_IMG_TYPES, ASSETS_BASE_PATH
from db_models.nollning_model import Nollning_DB
from services import user as user_service
from user.permission import Permission
from api_schemas.post_schemas import PostRead
import datetime

user_router = APIRouter()


@user_router.get("/admin/all/", response_model=list[AdminUserRead], dependencies=[Permission.require("view", "User")])
def admin_get_all_users(db: DB_dependency):
    all_users = db.query(User_DB).all()
    return all_users


@user_router.get("/admin/{user_id}", response_model=AdminUserRead, dependencies=[Permission.require("view", "User")])
def admin_get_user(user_id: int, db: DB_dependency):
    user = db.query(User_DB).filter(User_DB.id == user_id).one_or_none()
    if not user:
        raise HTTPException(404, detail="User not found")

    return user


@user_router.delete("/admin/{user_id}", dependencies=[Permission.require("super", "User")])
async def admin_delete_user(
    user_id: int,
    db: DB_dependency,
    user_manager: BaseUserManager[User_DB, int] = Depends(USERS.get_user_manager),
):
    user = db.query(User_DB).filter(User_DB.id == user_id).one_or_none()
    if not user:
        raise HTTPException(404, detail="User not found")
    if user.is_member:
        raise HTTPException(403, detail="User is member")
    if not (len(user.posts) == 0):
        raise HTTPException(403, detail="User has posts")
    await user_manager.delete(user)
    return Response(None, status.HTTP_204_NO_CONTENT)


@user_router.get("/me", response_model=AdminUserRead)
def get_me(user: Annotated[User_DB, Permission.primitive()]):
    return user


@user_router.patch("/update/me", response_model=AdminUserRead)
def update_self(data: UserUpdate, current_user: Annotated[User_DB, Permission.base()], db: DB_dependency):
    return user_service.update_user(current_user.id, data, db)


@user_router.patch(
    "/admin/update/{user_id}", response_model=AdminUserRead, dependencies=[Permission.require("manage", "User")]
)
def admin_update_user(data: UserUpdate, user_id: int, db: DB_dependency):
    return user_service.update_user(user_id, data, db)


@user_router.patch(
    "/admin/member-status/{user_id}", response_model=AdminUserRead, dependencies=[Permission.require("manage", "User")]
)
def update_user_status(user_id: int, data: UpdateUserMember, db: DB_dependency):
    return user_service.update_user_status(user_id, data, db)


@user_router.patch(
    "/admin/member-status", response_model=list[AdminUserRead], dependencies=[Permission.require("manage", "User")]
)
def update_multiple_users_status(data: list[UpdateUserMemberMultiple], db: DB_dependency):
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No users provided for status update")

    return user_service.update_multiple_users_status(data, db)


@user_router.patch(
    "/admin/user-posts/{user_id}",
    response_model=AdminUserRead,
    dependencies=[Permission.require("manage", "UserPost")],
)
def update_user_posts(user_id: int, data: UpdateUserPosts, db: DB_dependency):
    user = db.query(User_DB).filter(User_DB.id == user_id).one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    updated_user = user_service.update_user_posts(user, data, db)
    return updated_user


@user_router.get("/{user_id}", dependencies=[Permission.require("view", "User")], response_model=UserRead)
def get_user(user_id: int, db: DB_dependency):
    user = db.query(User_DB).filter(User_DB.id == user_id).one_or_none()
    if not user:
        raise HTTPException(404, detail="User not found")

    return user


@user_router.get("/posts/{user_id}", response_model=list[PostRead], dependencies=[Permission.require("view", "User")])
def get_user_posts(user_id: int, db: DB_dependency):
    user = db.query(User_DB).filter_by(id=user_id).one_or_none()
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return user.posts


# Verification routes can be found in auth_router.py
@user_router.get("/search/", response_model=list[UserRead], dependencies=[Permission.require("view", "User")])
def search_users(
    db: DB_dependency,
    name: Optional[str] = Query(default=None),
    program: Optional[str] = Query(default=None),
    start_year: Optional[int] = Query(default=None),
    exclude_ids: Optional[list[int]] = Query(default=None),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0),
):
    users = db.query(User_DB)

    if name:
        if len(name) < 3:
            raise HTTPException(400, "Too few characters, search string must be at least 3.")
        name_filters: list[ColumnElement[bool]] = []
        for term in name.split(" "):
            name_filters.append(or_(User_DB.first_name.ilike(f"%{term}%"), User_DB.last_name.ilike(f"%{term}%")))
        users = users.filter(and_(*name_filters))

    if program:
        users = users.filter_by(program=program)

    if start_year:
        users = users.filter_by(start_year=start_year)

    if exclude_ids:
        users = users.filter(~(User_DB.id.in_(exclude_ids)))

    return users.offset(offset).limit(limit).all()


@user_router.post("/image", dependencies=[Depends(rate_limit())])
async def post_user_image(user: Annotated[User_DB, Permission.member()], db: DB_dependency, image: UploadFile = File()):

    if image:

        await validate_image(image)

        filename: str = str(image.filename)
        _, ext = os.path.splitext(filename)

        ext = ext.lower()

        if ext not in ALLOWED_EXT:
            raise HTTPException(400, "file extension not allowed")

        dest_path = Path(f"{ASSETS_BASE_PATH}/users/{user.id}{ext}")

        dest_path.write_bytes(image.file.read())


@user_router.get("/{user_id}/image/{size}", dependencies=[Permission.member()])
def get_user_image(user_id: int, size: ALLOWED_IMG_TYPES, db: DB_dependency):

    dims = ALLOWED_IMG_SIZES[size]

    user = db.query(User_DB).get(user_id)
    if not user:
        raise HTTPException(404, "No image for this user")

    asset_dir = Path(f"{ASSETS_BASE_PATH}") / "users"

    matches = list(asset_dir.glob(f"{user.id}.*"))
    if not matches:
        raise HTTPException(404, "Image not found")

    filename = matches[0].name

    internal = f"/internal/{dims}{ASSETS_BASE_PATH}/users/{filename}"

    return Response(status_code=200, headers={"X-Accel-Redirect": internal})


@user_router.get("/{user_id}/image/stream", dependencies=[Permission.member(), Depends(rate_limit())])
def get_user_image_stream(user_id: int, db: DB_dependency):
    user = db.query(User_DB).get(user_id)
    if not user:
        raise HTTPException(404, "No image for this user")

    asset_dir = Path(f"{ASSETS_BASE_PATH}") / "users"

    matches = list(asset_dir.glob(f"{user.id}.*"))
    if not matches:
        raise HTTPException(404, "Image not found")

    filename = matches[0].name

    internal = f"/{ASSETS_BASE_PATH}/users/{filename}"

    return FileResponse(internal)


@user_router.get("/user_priorities/me", response_model=list[str])
def get_my_priorities(me: Annotated[User_DB, Permission.member()], db: DB_dependency):
    priorities: list[str] = []

    for post in me.posts:
        priorities.append(post.name_sv)

    now = datetime.datetime.now(datetime.timezone.utc)

    nollning = db.query(Nollning_DB).filter(Nollning_DB.year == now.year).one_or_none()

    found = False

    if nollning:
        for nollningGroup in nollning.nollning_groups:
            for groupUser in nollningGroup.group.group_users:
                if me.id == groupUser.user_id:
                    if nollningGroup.group.group_type == "Mentor":
                        if groupUser.group_user_type == "Mentor":
                            priorities.append("Gruppfadder")
                        elif groupUser.group_user_type == "Mentee":
                            priorities.append("Nolla")
                    elif nollningGroup.group.group_type == "Mission":
                        if groupUser.group_user_type == "Mentor":
                            priorities.append("Uppdragsfadder")
                        elif groupUser.group_user_type == "Mentee":
                            priorities.append("Nolla")
                    found = True
                    break
            if found:
                break

    return priorities
