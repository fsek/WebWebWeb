# With these we define special permissions beyond being just a logged-in and verified user
# Each Post can have several permissions.
# Action/Target division is just for our convenience.
from typing import Literal

PermissionAction = Literal["view", "manage"]
PermissionTarget = Literal["Event", "User", "Post"]

# M: dict[PermissionTarget, str] = {
# "Event": db_models.Event_DB,

# }
