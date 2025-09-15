from datetime import datetime, timedelta
import os
from typing import Annotated, Literal, TypeAlias
from pydantic import AfterValidator
from enum import Enum


def force_utc(date: datetime):
    if date.utcoffset() != timedelta(0):
        raise ValueError(f"datetime must be UTC. utcoffset was {date.utcoffset()}")
    return date


# use this as datetime type in schemas. This way we force frontend to specify their time in UTC
datetime_utc: TypeAlias = Annotated[datetime, AfterValidator(force_utc)]


# a user who is a member can have some member types
MEMBER_TYPE = Literal["member", "novice", "mentor, photographer"]


ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".gif"}

ALLOWED_IMG_TYPES = Literal["small", "medium", "large", "original"]

ALLOWED_IMG_SIZES = {"small": "200x200", "medium": "500x500", "large": "1000x1000", "original": "0x0"}


# With these we define special permissions beyond being just a logged-in and verified user
# Action/Target division is just for our convenience.
# These lists only define possible values.
# db-objects which pair one action and target must be created to give permissions to posts

# WARNING: Remove only an item from these if db-objects using the item have been deleted.
# Adding to them is always safe though.

PERMISSION_TYPE = Literal["view", "manage", "super"]
PERMISSION_TARGET = Literal[
    "Event",
    "Document",
    "User",
    "Post",
    "UserPost",
    "Permission",
    "News",
    "Song",
    "Ads",
    "Gallery",
    "Car",
    "Cafe",
    "Election",
    "Groups",
    "AdventureMissions",
    "Nollning",
    "UserDoorAccess",
    "Tags",
    "Council",
    "RoomBookings",
    "Moosegame",
    "MailAlias",
]

# This is a little ridiculous now, but if we have many actions, this is a neat system.
# This one is to make one action eg. "be_a_god" mean several actions eg. "view", "manage", "know_everything",
# PermissionCompoundActions: dict[PermissionAction, list[PermissionAction]] = {"manage": ["view"]}


GROUP_TYPE = Literal["Mentor", "Mission", "Default", "Committee"]
GROUP_USER_TYPE = Literal["Mentor", "Mentee", "Default"]

# All doors the guild manages access to.

DOOR_ACCESSES = Literal[
    "Ledningscentralen",
    "Ambassaden",
    "Syster Kents",
    "Hilbert Cafe",
    "Cafeförrådet",
    "Pubförrådet",
    "Sopkomprimatorn",
    "Arkivet",
]

# Standard food preferences the user can put on their account

FOOD_PREFERENCES = Literal["Vegetarian", "Vegan", "Pescetarian", "Milk", "Gluten"]

DRINK_PACKAGES = Literal["None", "AlcoholFree", "Alcohol"]

ALCOHOL_EVENT_TYPES = Literal["Alcohol", "Alcohol-Served", "None"]

EVENT_DOT_TYPES = Literal["None", "Single", "Double"]

PROGRAM_TYPE = Literal["Oklart", "F", "Pi", "N"]

ROOMS = Literal["LC", "Alumni", "SK", "Hilbert Cafe"]

MISSION_CONFIRMED_TYPES = Literal["Accepted", "Failed", "Review"]

ASSETS_BASE_PATH = os.getenv("ASSETS_BASE_PATH")


# Election timing types
POST_ELECTION_SEMESTERS = Literal["HT", "VT", "HT and VT", "Other"]

# Guild = sektionsmöte, Board = styrelsen vid valmöte för funktionärer, Educational Council = studierådet, Board Intermediate = mellanliggande valmöte
ELECTION_ELECTORS = Literal["Guild", "Board", "Educational Council", "Board Intermediate", "Other"]

ELECTION_SEMESTERS = Literal["HT", "VT", "Other"]
