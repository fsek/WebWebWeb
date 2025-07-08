from typing import Annotated
import uuid

import redis
from fastapi import APIRouter, Depends, HTTPException, status
from database import DB_dependency, get_redis
from db_models.user_model import User_DB
from api_schemas.user_schemas import AdminUserRead, UpdateUserMember, UserUpdate, UserRead
from mailer.verification_mailer import verification_mailer
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
def get_me(user: Annotated[User_DB, Permission.base()]):
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


@user_router.post("/verification", response_model=None, dependencies=[Permission.primitive()])
async def send_verfication(me: Annotated[User_DB, Permission.primitive()], redis: redis.Redis = Depends(get_redis)):

    token = str(uuid.uuid4())
    await redis.setex(f"verif:{token}", 24 * 3600, me.id)

    verification_mailer(me, token)


@user_router.post(
    "/verification/{token}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
async def verify_mail(
    token: str,
    db: DB_dependency,
    redis: redis.Redis = Depends(get_redis),
):

    user_id = await redis.get(f"verif:{token}")
    if not user_id:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired verification token",
        )

    redis.delete(f"verif:{token}")

    user_id = int(user_id)

    user = db.query(User_DB).filter(User_DB.id == user_id).one_or_none()

    if not user:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)

    user.is_verified = True
    db.commit()
    db.refresh(user)

    return user
