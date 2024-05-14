from fastapi import APIRouter
from api_schemas.mentor_group_schema import MentorGroupCreate, MentorGroupRead
from database import DB_dependency
from user.permission import Permission
from services.mentor_group_service import add_to_mentor_group, get_mentor_group, post_mentor_group
from typing import TYPE_CHECKING, Annotated

if TYPE_CHECKING:
    from db_models.user_model import User_DB

mentor_group_router = APIRouter()


@mentor_group_router.post("/", dependencies=[Permission.require("manage", "Groups")])
def upload_mentor_group(db: DB_dependency, data: MentorGroupCreate):
    return post_mentor_group(db, data)


@mentor_group_router.get("/{id}", dependencies=[Permission.require("view", "Groups")], response_model=MentorGroupRead)
def get_single_mentor_group(db: DB_dependency, id: int):
    return get_mentor_group(db, id)


@mentor_group_router.post("{id}", dependencies=[Permission.require("manage", "Groups")])
def add_user_to_mentor_group(db: DB_dependency, id: int, user_id: int, mentor_type: str):
    return add_to_mentor_group(db, id, user_id, mentor_type)
