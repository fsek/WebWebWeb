from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from api_schemas.post_schemas import PostRead
from database import DB_dependency, get_db
from db_models.permission_model import Permission_DB
from db_models.post_model import Post_DB
from api_schemas.permission_schemas import PermissionCreate, PermissionRead, UpdatePermission, PermissionRemove
from services.permission_service import assign_permission, unassign_permission
from user.permission import Permission

permission_router = APIRouter()


@permission_router.get(
    "/", response_model=list[PermissionRead], dependencies=[Permission.require("view", "Permission")]
)
def get_all_permissions(db: Annotated[Session, Depends(get_db)]):
    res = db.query(Permission_DB).all()
    return res


# Create a new permission which later can be assigned to posts
@permission_router.post("/", response_model=PermissionRead, dependencies=[Permission.require("manage", "Permission")])
def create_permission(perm_data: PermissionCreate, db: Annotated[Session, Depends(get_db)]):
    num_existing = (
        db.query(Permission_DB)
        .filter(Permission_DB.action == perm_data.action, Permission_DB.target == perm_data.target)
        .count()
    )
    # if there already is this exact permission, dont create
    if num_existing > 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="This permission already exists")

    perm = Permission_DB(action=perm_data.action, target=perm_data.target)
    db.add(perm)
    db.commit()
    return perm


# Assign or unassign a permission on a post
@permission_router.post(
    "/update-permission", dependencies=[Permission.require("manage", "Permission")], response_model=PostRead
)
def change_post_permission(perm_data: UpdatePermission, db: DB_dependency):
    post = db.query(Post_DB).filter(Post_DB.id == perm_data.post_id).one_or_none()
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if perm_data.change == "add":
        assign_permission(post, perm_data.permission_id, db)
    elif perm_data.change == "remove":
        unassign_permission(post, perm_data.permission_id, db)

    return post


# Remove a permission completely
@permission_router.delete("/", response_model=PermissionRead, dependencies=[Permission.require("manage", "Permission")])
def remove_permission(perm_data: PermissionRemove, db: Annotated[Session, Depends(get_db)]):
    perm = (
        db.query(Permission_DB)
        .filter(Permission_DB.action == perm_data.action, Permission_DB.target == perm_data.target)
        .one_or_none()
    )

    if perm == None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No such permission exists")

    db.delete(perm)
    db.commit()
    return perm
