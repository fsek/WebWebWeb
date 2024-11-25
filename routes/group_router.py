from fastapi import APIRouter
from api_schemas.group_schema import GroupAddUser, GroupCreate, GroupRead
from database import DB_dependency
from helpers.types import GROUP_TYPE, GROUP_USER_TYPE
from user.permission import Permission
from services.group_service import add_to_group, edit_group, get_group, post_group, get_all_groups
from typing import TYPE_CHECKING, Annotated, Literal

if TYPE_CHECKING:
    from db_models.user_model import User_DB

group_router = APIRouter()


@group_router.post("/", dependencies=[Permission.require("manage", "Groups")], response_model=GroupRead)
def upload_mentor_group(db: DB_dependency, data: GroupCreate):
    return post_group(db, data)


@group_router.get("/", dependencies=[Permission.require("view", "Groups")], response_model=list[GroupRead])
def get_groups(db: DB_dependency, group_type: GROUP_TYPE | None = None):
    return get_all_groups(db, group_type)


@group_router.get("/{id}", dependencies=[Permission.require("view", "Groups")], response_model=GroupRead)
def get_single_group(db: DB_dependency, id: int):
    return get_group(db, id)


@group_router.post("/add_user/{id}", dependencies=[Permission.require("manage", "Groups")], response_model=GroupRead)
def add_user_to_mentor_group(db: DB_dependency, id: int, data: GroupAddUser):
    return add_to_group(db, id, data)


@group_router.patch("/{id}", dependencies=[Permission.require("manage", "Groups")], response_model=GroupRead)
def patch_group(db: DB_dependency, id: int, data: GroupCreate):
    return edit_group(db, id, data)
