from fastapi import APIRouter, HTTPException
from database import DB_dependency
from db_models.user_door_access_model import UserDoorAccess_DB
from db_models.post_model import Post_DB
from helpers.types import DOOR_ACCESSES
from typing import get_args
import datetime


access_serve_router = APIRouter()


def _validate_door_parameter(door: str) -> None:
    """Validate that the door parameter is provided and exists in our system."""
    if not door:
        raise HTTPException(status_code=400, detail="Door parameter is required")
    if door not in get_args(DOOR_ACCESSES):
        raise HTTPException(status_code=404, detail=f"Door {door} not found")


def _get_user_access_stil_ids(db: DB_dependency, door: str) -> list[str]:
    """Get STIL IDs for users with direct access to the door."""
    user_accesses = db.query(UserDoorAccess_DB).filter(UserDoorAccess_DB.door == door).all()
    stil_ids: list[str] = []
    now = datetime.datetime.now(datetime.timezone.utc)

    for access in user_accesses:
        if access.user and access.user.stil_id:
            if access.starttime and access.starttime > now:
                continue
            if access.endtime and access.endtime < now:
                continue
            stil_ids.append(access.user.stil_id)

    return stil_ids


def _get_post_access_stil_ids(db: DB_dependency, door: str) -> list[str]:
    """Get STIL IDs for users with access through posts."""
    posts = db.query(Post_DB).all()
    post_stil_ids: list[str] = []

    for post in posts:
        # Check if this post grants access to the requested door
        if post.post_door_accesses:
            door_has_access = any(post_door_access.door == door for post_door_access in post.post_door_accesses)
            if door_has_access and post.users:
                # Add all users from this post, filtering out None values
                user_stil_ids = [user.stil_id for user in post.users if user and user.stil_id]
                post_stil_ids.extend(user_stil_ids)

    return post_stil_ids


@access_serve_router.get("/{door}", response_model=list[str])
def get_all_access_ids(door: str, db: DB_dependency) -> list[str]:
    """
    Get all STIL IDs that have access to a specific door.

    This endpoint allows the serving of LU's servers by providing STIL IDs for door systems.
    Access can be granted through:
    1. Direct user door access assignments
    2. Post (group) memberships that include door access

    The actual serving is done on the frontend.
    TODO: Ideally we should communicate with LU to get them some better non-public API.
    """
    _validate_door_parameter(door)

    # Get users with direct door access
    direct_access_ids = _get_user_access_stil_ids(db, door)

    # Get users with access through post memberships
    post_access_ids = _get_post_access_stil_ids(db, door)

    # Combine, remove duplicates, and sort alphabetically
    # sort to prevent attacks based on order
    all_access_ids = sorted(set(direct_access_ids + post_access_ids))

    # Remove all stil-ids which are not alphanumeric with dashes,
    # just a failsafe if stil_id is not set properly since we will be putting these in html
    for stil_id in all_access_ids:
        if not stil_id or not stil_id.replace("-", "").isalnum():
            all_access_ids.remove(stil_id)

    return all_access_ids
