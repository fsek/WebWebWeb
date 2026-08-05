from datetime import UTC, datetime
from typing import get_args
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from db_models.event_model import Event_DB
from db_models.event_user_model import EventUser_DB
from db_models.user_model import User_DB
from db_models.group_model import Group_DB
from db_models.group_user_model import GroupUser_DB
from api_schemas.event_signup_schemas import EventSignupCreate, EventSignupUpdate
from helpers.constants import DEFAULT_USER_PRIORITY
from helpers.types import GROUP_TYPE


def signup_to_event(event: Event_DB, user: User_DB, data: EventSignupCreate, manage_permission: bool, db: Session):
    now = datetime.now(UTC)

    if not event.can_signup:
        raise HTTPException(400, detail="Cannot signup to this event")

    if (event.closed) and (manage_permission == False):
        raise HTTPException(400, detail="Event is closed")

    if (event.signup_start > now) and (manage_permission == False):
        raise HTTPException(400, detail="Event signup has not opened yet")

    if (event.signup_end < now) and (manage_permission == False):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event signup deadline is passed")

    if (
        db.query(EventUser_DB)
        .filter((EventUser_DB.user_id == data.user_id) & (EventUser_DB.event_id == event.id))
        .one_or_none()
    ):
        raise HTTPException(400, detail="User already signed up to chosen event")

    if (
        manage_permission == False
        and data.group_name is not None
        and not is_group_allowed(event, user, data.group_name)
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User cannot sign up with this group")

    signup = EventUser_DB(user=user, user_id=user.id, event=event, event_id=event.id)

    for var, value in vars(data).items():
        setattr(signup, var, value) if value else None

    if not event.drink_package:
        signup.drinkPackage = "None"

    db.add(signup)

    event.signup_count += 1

    db.commit()

    return signup


def signoff_from_event(
    event: Event_DB,
    user_id: int,
    manage_permission: bool,
    db: Session,
):
    now = datetime.now(UTC)
    if event.signup_end < now and manage_permission == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event signup deadline is passed")
    signup = db.query(EventUser_DB).filter_by(user_id=user_id, event_id=event.id).one_or_none()
    if signup is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    db.delete(signup)

    event.signup_count -= 1

    db.commit()
    return signup


def update_event_signup(event: Event_DB, data: EventSignupUpdate, user_id: int, manage_permission: bool, db: Session):
    now = datetime.now(UTC)
    if event.signup_end < now and manage_permission == False:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Event signup deadline is passed")
    signup = db.query(EventUser_DB).filter_by(user_id=user_id, event_id=event.id).one_or_none()
    if signup is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    if (
        manage_permission == False
        and data.group_name is not None
        and not is_group_allowed(event, db.query(User_DB).filter(User_DB.id == user_id).one(), data.group_name)
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User cannot sign up with this group")

    for var, value in vars(data).items():
        if var == "priority" and not value:
            setattr(signup, "priority", DEFAULT_USER_PRIORITY)
        elif var == "group_name" and not value:
            setattr(signup, "group_name", None)
        else:
            setattr(signup, var, value) if value else None

    if not event.drink_package:
        signup.drinkPackage = "None"

    db.commit()
    db.refresh(event)
    return signup


def check_me_signup(event_id: int, me: User_DB, db: Session):
    signup = (
        db.query(EventUser_DB)
        .filter((EventUser_DB.user_id == me.id) & (EventUser_DB.event_id == event_id))
        .one_or_none()
    )
    if not signup:
        raise HTTPException(404, detail="Signup not found")

    return signup


def get_allowed_groups(event: Event_DB, user: User_DB):
    allowed_groups: list[Group_DB] = []
    if event.is_nollning_event:
        allowed_group_types = event.mentor_group_types or list(get_args(GROUP_TYPE))
        for gu in user.group_users:
            if _is_group_allowed(gu, event, allowed_group_types):
                allowed_groups.append(gu.group)
    else:
        allowed_groups = user.groups

    return allowed_groups


def is_group_allowed(event: Event_DB, user: User_DB, group_name: str | None):
    if event.is_nollning_event:
        allowed_group_types = event.mentor_group_types or list(get_args(GROUP_TYPE))
        is_event_allowed = False
        for gu in user.group_users:
            if group_name == gu.group.name:
                if _is_group_allowed(gu, event, allowed_group_types):
                    is_event_allowed = True
                break

        if not is_event_allowed:
            return False

    return True


def _is_group_allowed(gu: GroupUser_DB, e: Event_DB, agt: list[GROUP_TYPE]):
    if not any(n.year == datetime.now().year for n in gu.group.nollnings):
        return False

    if gu.group.group_type in agt:
        return True
    elif (gu.group_user_type == "Mentor") and e.allow_other_mentors:
        return True
    return False
