from typing import Annotated
from db_models import permission_model
from fastapi import APIRouter, HTTPException, status
from api_schemas.base_schema import BaseSchema
from database import DB_dependency
from db_models.user_model import User_DB
from api_schemas.user_schemas import UpdateUserMember, UserUpdate, UserRead
from services import user as user_service
from user.permission import Permission
from api_schemas.post_schemas import PostRead

user_router = APIRouter()


@user_router.get("/", response_model=list[UserRead], dependencies=[Permission.require("view", "User")])
def get_all_users(db: DB_dependency):
    all_users = db.query(User_DB).all()
    return all_users


@user_router.get("/me", response_model=UserRead)
def get_me(user: Annotated[User_DB, Permission.base()]):
    return user


@user_router.patch("/update/me", response_model=UserRead)
def update_self(data: UserUpdate, current_user: Annotated[User_DB, Permission.base()], db: DB_dependency):
    return user_service.update_user(current_user.id, data, db)


@user_router.patch("/update/{user_id}", response_model=UserRead, dependencies=[Permission.require("manage", "User")])
def update_user(data: UserUpdate, user_id: int, db: DB_dependency):
    return user_service.update_user(user_id, data, db)


@user_router.patch(
    "/member-status/{user_id}", response_model=UserRead, dependencies=[Permission.require("manage", "User")]
)
def update_user_status(user_id: int, data: UpdateUserMember, db: DB_dependency):
    return user_service.update_user_status(user_id, data, db)


@user_router.get("/posts/{user_id}", response_model=list[PostRead], dependencies=[Permission.require("view", "User")])
def get_user_posts(user_id: int, db: DB_dependency):
    user = db.query(User_DB).filter_by(id=user_id).one_or_none()
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return user.posts
