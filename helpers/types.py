from datetime import datetime, timedelta
from typing import Annotated, Literal, TypeAlias
from pydantic import AfterValidator


def force_utc(date: datetime):
    if date.utcoffset() != timedelta(0):
        raise ValueError(f"datetime must be UTC. utcoffset was {date.utcoffset()}")
    return date


# use this as datetime type in schemas. This way we force frontend to specify their time in UTC
datetime_utc: TypeAlias = Annotated[datetime, AfterValidator(force_utc)]


# a user who is a member can have some member types
MEMBER_TYPE = Literal["member", "novice", "mentor, photographer"]
MEMBER_ROLES = Literal["photographer", "ordförande", "dinmamma"]

# With these we define special permissions beyond being just a logged-in and verified user
# Action/Target division is just for our convenience.
# These lists only define possible values.
# db-objects which pair one action and target must be created to give permissions to posts

# WARNING: Remove only an item from these if db-objects using the item have been deleted.
# Adding to them is always safe though.

PERMISSION_TYPE = Literal["view", "manage"]
PERMISSION_TARGET = Literal[
    "Event",
    "Document",
    "User",
    "Post",
    "Permission",
    "News",
    "Song",
    "Ads",
    "Gallery",
    "Car",
    "Cafe",
    "Election",
    "Groups",
    "Adventure Missions",
    "Nollning",
    "UserDoorAccess",
    "Tags",
    "Council",
    "Rooms",
]

# This is a little ridiculous now, but if we have many actions, this is a neat system.
# This one is to make one action eg. "be_a_god" mean several actions eg. "view", "manage", "know_everything",
# PermissionCompoundActions: dict[PermissionAction, list[PermissionAction]] = {"manage": ["view"]}


GROUP_TYPE = Literal["Mentor", "Mission", "Default", "Committee"]
GROUP_USER_TYPE = Literal["Mentor", "Mentee", "Default"]

# All doors the guild manages access to.

DOOR_ACCESSES = Literal[
    "LC", "Bunkern", "Syster Kents", "Cafét", "Caféförrådet", "Pubförrådet", "Containern", "Arkivet"
]

# Standard food preferences the user can put on their account

FOOD_PREFERENCES = Literal["Vegetarian", "Vegan", "Pescetarian", "Mjölkallergi", "Gluten"]

DRINK_PACKAGES = Literal["None", "AlcoholFree", "Alcohol"]
