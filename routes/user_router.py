from typing import Annotated
from fastapi import APIRouter, HTTPException, status
from api_schemas.base_schema import BaseSchema
from database import DB_dependency
from db_models.user_model import User_DB
from api_schemas.user_schemas import MeUpdate, UserRead
from user.permission import Permission

user_router = APIRouter()


@user_router.get("/", response_model=list[UserRead])
def get_all_users(db: DB_dependency):
    all_users = db.query(User_DB).all()
    return all_users


@user_router.get("/me", response_model=UserRead)
def get_me(user: Annotated[User_DB, Permission.base()]):
    return user


@user_router.patch("/me", response_model=UserRead)
def update_me(data: MeUpdate, current_user: Annotated[User_DB, Permission.base()], db: DB_dependency):
    # Since we edit user, look it up using "db" and not from permission so were are in same session
    me = db.query(User_DB).filter_by(id=current_user.id).one()

    # not elegant, will have to find better wat for future update routes
    if data.firstname:
        me.firstname = data.firstname
    if data.lastname:
        me.lastname = data.lastname

    db.commit()
    return current_user


class UpdateUserMember(BaseSchema):
    is_member: bool


@user_router.patch("/{user_id}/member-status", dependencies=[Permission.require("manage", "User")])
def update_user(user_id: int, data: UpdateUserMember, db: DB_dependency):
    user = db.query(User_DB).filter_by(id=user_id).one_or_none()
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    user.is_member = data.is_member

    db.commit()
    return user


# TODO update your own stuff, delete routes
