from typing import Annotated, Any, Dict, cast
from fastapi import APIRouter, HTTPException, status
from database import DB_dependency
from db_models.user_model import User_DB
from schemas.user_schemas import BaseSchema, MeUpdate, UserRead
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
    update_dict = data.model_dump(exclude_none=True, exclude_unset=True)
    # Warning: this is assuming we don't need any validation above just setting attributes directly.
    # if no db column definitions or custom validates directives cover our needed validation on fields allowed into this route then we gotta add it here

    db.query(User_DB).filter_by(id=current_user.id).values(**update_dict)
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
