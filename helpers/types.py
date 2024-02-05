from typing import Literal

# a user who is a member can have some member types
MEMBER_TYPE = Literal["member", "novice", "mentor"]

#
#
#


# With these we define special permissions beyond being just a logged-in and verified user
# Action/Target division is just for our convenience.
# These lists only define possible values.
# db-objects which pair one action and target must be created to give permissions to posts

# WARNING: Remove only an item from these if db-objects using the item have been deleted.
# Adding to them is always safe though.

PERMISSION_TYPE = Literal["view", "manage"]
PERMISSION_TARGET = Literal["Event", "User", "Post", "Permission", "News"]

# This is a little ridiculous now, but if we have many actions, this is a neat system.
# This one is to make one action eg. "be_a_god" mean several actions eg. "view", "manage", "know_everything",
# PermissionCompoundActions: dict[PermissionAction, list[PermissionAction]] = {"manage": ["view"]}
