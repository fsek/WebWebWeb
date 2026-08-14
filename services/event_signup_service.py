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
from helpers.constants import DEFAULT_USER_PRIORITY, NOLLNING_PRIORITIES
from helpers.types import GROUP_TYPE
from services.nollning_service import get_user_nollning_priorities


def get_allowed_signup_priorities(event: Event_DB, user: User_DB, db: Session) -> set[str]:
    """The priorities the user may sign up to the event with: the event's own priorities which the
    user actually holds, plus the default priority which everyone falls back on."""
    allowed = {DEFAULT_USER_PRIORITY}
    if not event.priorities:
        return allowed

    user_priorities = {post.name_sv for post in user.posts} | get_user_nollning_priorities(db, user)

    return allowed | ({p.priority for p in event.priorities} & user_priorities)


def check_priority_allowed(event: Event_DB, user: User_DB, priority: str, db: Session):
    """Signups are only ever stored with a priority the user really has, so that the stored
    signups can be trusted."""
    if priority not in get_allowed_signup_priorities(event, user, db):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User cannot sign up with this priority")


def user_matches_existing_event_post_priorities(user: User_DB, event: Event_DB):
    """Only true if a user has a post which matches one of the event's priorities,
    and that priority match is not a nollning priority (which are tied to groups instead of posts)."""
    if not event.priorities:
        return False

    event_post_priorities = {p.priority for p in event.priorities if p.priority not in NOLLNING_PRIORITIES}

    return any(post.name_sv in event_post_priorities for post in user.posts)


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

    if manage_permission == False and not is_group_allowed(event, user, data.group_name):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User cannot sign up with this group")

    if manage_permission == False and data.priority:  # a falsy priority just means the default one
        check_priority_allowed(event, user, data.priority, db)

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

    # Only fields the client actually sent are considered.
    updates = data.model_dump(exclude_unset=True, exclude={"user_id"})

    if "group_name" in updates and not updates["group_name"]:  # if falsy
        updates["group_name"] = None

    # Only authorize the group when the client asked to change it, otherwise an update that leaves
    # the group alone would be rejected on nollning events for not carrying a group at all.
    if (
        manage_permission == False
        and "group_name" in updates
        and not is_group_allowed(event, signup.user, updates["group_name"])
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User cannot sign up with this group")

    # priority and drinkPackage are not nullable in the database, so a null means "back to default"
    if "priority" in updates and not updates["priority"]:  # if falsy
        updates["priority"] = DEFAULT_USER_PRIORITY

    if manage_permission == False and "priority" in updates and updates["priority"] != signup.priority:
        check_priority_allowed(event, signup.user, updates["priority"], db)

    if "drinkPackage" in updates and updates["drinkPackage"] is None:
        del updates["drinkPackage"]  # None is not a valid value ("None" is), so leave the old value in place

    for var, value in updates.items():
        setattr(signup, var, value)

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
        if group_name is None:
            # Without a group the user has to qualify through a post priority instead,
            # since nollning priorities are tied to a group
            return user_matches_existing_event_post_priorities(user, event)

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
    if gu.group.group_type in agt:
        return True
    elif (gu.group_user_type == "Mentor") and e.allow_other_mentors:
        return True
    return False
