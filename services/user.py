from typing import get_args

from api_schemas.user_schemas import UserUpdate, UpdateUserMember
from database import DB_dependency
from db_models.user_model import User_DB
from fastapi import HTTPException, status
from sqlalchemy.exc import DataError, NoResultFound, MultipleResultsFound
import re
from helpers.types import FOOD_PREFERENCES


def check_stil_id(s: str) -> bool:
    if not len(s) == 10:
        return False
    pattern = r"^[a-z]{2}\d{4}[a-z]{2}-s$"
    return bool(re.fullmatch(pattern, s))


def condition(model, asset):
    return model == asset.get("id")


def update_user(user_id: int, data: UserUpdate, db: DB_dependency):
    try:
        user = db.query(User_DB).filter_by(id=user_id).one()
    except NoResultFound:
        raise HTTPException(404, detail="User not found")
    except MultipleResultsFound:
        # Probably shouldn't happen
        print("ERROR: Multiple users found with the same ID:", user_id)
        raise HTTPException(500, detail="Multiple users found with the same ID")

    if data.stil_id:
        if not check_stil_id(data.stil_id):
            raise HTTPException(400, detail="Invalid stil-id")
        user.stil_id = data.stil_id

    VALID_FOOD_PREFS = set(get_args(FOOD_PREFERENCES))

    if data.standard_food_preferences:
        for item in data.standard_food_preferences:
            if item not in VALID_FOOD_PREFS:
                raise HTTPException(400, detail=f"{item} not a valid standard food preference")

    for var, val in vars(data).items():
        setattr(user, var, val) if val else None

    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST)

    return user


def update_user_status(user_id: int, data: UpdateUserMember, db: DB_dependency):
    user = db.query(User_DB).filter_by(id=user_id).one_or_none()
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    user.is_member = data.is_member

    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST)
    return user
