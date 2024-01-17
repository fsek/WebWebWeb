from typing import Annotated
from fastapi import APIRouter
from database import DB_dependency
from db_models.user_model import User_DB

from schemas.user_schemas import UserRead
from user.permission import Permission

user_router = APIRouter()


@user_router.get("/", response_model=list[UserRead])
def get_all_users(db: DB_dependency):
    all_users = db.query(User_DB).all()
    return all_users


@user_router.get("/me", response_model=UserRead)
def get_me(user: Annotated[User_DB, Permission.base()]):
    return user


# TODO update, delete routes
