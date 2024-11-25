from fastapi import HTTPException
from sqlalchemy.orm import Session
from api_schemas.group_schema import GroupAddUser, GroupCreate, GroupRead
from db_models.group_model import Group_DB
from db_models.group_user_model import GroupUser_DB
from db_models.user_model import User_DB
from sqlalchemy.exc import DataError

from helpers.types import GROUP_USER_TYPE


def post_group(db: Session, data: GroupCreate):
    group = Group_DB(name=data.name, group_type=data.group_type)

    db.add(group)

    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(400, "Group type not allowed")

    return group


def get_all_groups(db: Session, group_type: str | None):
    if not group_type:
        groups = db.query(Group_DB).all()
    else:
        groups = db.query(Group_DB).filter(Group_DB.group_type == group_type).all()

    return groups


def get_group(db: Session, id: int):
    group = db.query(Group_DB).filter(Group_DB.id == id).one_or_none()
    if group == None:
        raise HTTPException(404, detail="Group not found")

    return group


def add_to_group(db: Session, id: int, data: GroupAddUser):
    group1 = db.query(Group_DB).filter(Group_DB.id == id).one_or_none()

    if group1 == None:
        raise HTTPException(404, detail="Group not found")

    user1 = db.query(User_DB).filter(User_DB.id == data.user_id).one_or_none()

    if user1 == None:
        raise HTTPException(404, detail="User not found")

    for user in group1.group_users:
        if user.user_id == user1.id:
            raise HTTPException(400, detail="User already in group")

    group_user = GroupUser_DB(
        user=user1, user_id=user1.id, group=group1, group_id=group1.id, group_user_type=data.group_user_type
    )

    db.add(group_user)
    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(404, detail="Invalid group_user type")

    return group1


def edit_group(db: Session, id: int, data: GroupCreate):
    group = db.query(Group_DB).filter(Group_DB.id == id).one_or_none()

    if not group:
        raise HTTPException(404, detail="Mission not found")

    for var, value in vars(data).items():
        setattr(group, var, value) if value else None

    db.commit()
    db.refresh(group)

    return group
