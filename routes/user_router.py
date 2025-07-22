from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from database import DB_dependency
from db_models.user_model import User_DB
from api_schemas.user_schemas import AdminUserRead, UpdateUserMember, UserUpdate, UserRead
from services import user as user_service
from user.permission import Permission
from api_schemas.post_schemas import PostRead

user_router = APIRouter()


@user_router.get("/admin/all/", response_model=list[AdminUserRead], dependencies=[Permission.require("manage", "User")])
def admin_get_all_users(db: DB_dependency):
    all_users = db.query(User_DB).all()
    return all_users


@user_router.get("/admin/{user_id}", response_model=AdminUserRead, dependencies=[Permission.require("manage", "User")])
def admin_get_user(user_id: int, db: DB_dependency):
    user = db.query(User_DB).filter(User_DB.id == user_id).one_or_none()
    if not user:
        raise HTTPException(404, detail="User not found")

    return user


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
