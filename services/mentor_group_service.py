from fastapi import HTTPException
from sqlalchemy.orm import Session
from api_schemas.mentor_group_schema import MentorGroupCreate
from db_models.mentor_group_model import MentorGroup_DB
from db_models.nollning_user_model import NollningUser_DB
from db_models.user_model import User_DB
from sqlalchemy.exc import DataError


def post_mentor_group(db: Session, data: MentorGroupCreate):
    group = MentorGroup_DB(name=data.name, group_type=data.group_type)

    db.add(group)

    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(400, "Group type not allowed")

    return {"message": "group created successfully"}


def get_mentor_group(db: Session, id: int):
    group = db.query(MentorGroup_DB).filter(MentorGroup_DB.id == id).one_or_none()

    if group == None:
        raise HTTPException(404, detail="Group not found")

    return group


def add_to_mentor_group(db: Session, id: int, user_id: int, mentor_type: str):
    group1 = db.query(MentorGroup_DB).filter(MentorGroup_DB.id == id).one_or_none()

    if group1 == None:
        raise HTTPException(404, detail="Group not found")

    user1 = db.query(User_DB).filter(User_DB.id == user_id).one_or_none()

    if user1 == None:
        raise HTTPException(404, detail="User not found")

    nollnings_user = NollningUser_DB(
        user=user1, user_id=user1.id, group=group1, group_id=group1.id, nollning_user_type=mentor_type
    )

    db.add(nollnings_user)
    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(404, detail="Invalid mentor type")

    return {"message": f"{user1.first_name} {user1.last_name} added successfully to group {group1.name}"}
