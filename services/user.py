from typing import get_args
from api_schemas.user_schemas import UpdateUserMemberMultiple, UpdateUserPosts, UserUpdate, UpdateUserMember
from database import DB_dependency
from db_models.user_model import User_DB
from fastapi import HTTPException, status
from sqlalchemy.exc import DataError, NoResultFound, MultipleResultsFound
import re
from helpers.types import FOOD_PREFERENCES
from db_models.post_model import Post_DB


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

    if data.standard_food_preferences == []:
        setattr(user, "standard_food_preferences", data.standard_food_preferences)

    if data.other_food_preferences == "":
        setattr(user, "other_food_preferences", data.other_food_preferences)

    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="DataError")

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


def update_multiple_users_status(data: list[UpdateUserMemberMultiple], db: DB_dependency):
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No users provided for status update")

    updated_users: list[User_DB] = []
    for user_data in data:
        user = db.query(User_DB).filter_by(id=user_data.user_id).one_or_none()
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"User with id {user_data.user_id} not found")

        user.is_member = user_data.is_member
        updated_users.append(user)

    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Error updating user statuses")

    return updated_users


def update_user_posts(user: User_DB, update_posts: UpdateUserPosts, db: DB_dependency):
    post_ids = update_posts.post_ids
    if not post_ids:
        user.posts.clear()

    else:
        # Fetch all posts with the given IDs
        posts = db.query(Post_DB).filter(Post_DB.id.in_(post_ids)).all()
        posts_by_id = {post.id: post for post in posts}

        # Check if all post_ids exist in the database
        missing_post_ids = [post_id for post_id in post_ids if post_id not in posts_by_id]
        if missing_post_ids:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Posts with ids {missing_post_ids} not found")

        # Add new posts to the user
        for post_id in post_ids:
            post = posts_by_id[post_id]
            if post not in user.posts:
                user.posts.append(post)

        # Remove posts not in the new list
        posts_to_remove = [post for post in user.posts if post.id not in post_ids]
        for post in posts_to_remove:
            user.posts.remove(post)

    try:
        db.commit()
    except DataError:
        db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Error updating user posts")

    return user
