from typing import Literal
from helper_types.permission_types import PermissionAction, PermissionTarget
from schemas.user_schemas import BaseSchema


class PermissionRead(BaseSchema):
    id: int
    action: PermissionAction
    target: PermissionTarget
    # This could fail response validation if a permission is left in db but deleted in hardcoded.
    # alternative is to just say "str" for this schemas action and target


class PermissionCreate(BaseSchema):
    action: PermissionAction
    target: PermissionTarget


class UpdatePermission(BaseSchema):
    post_id: int
    change: Literal["add", "remove"]
    permission_id: int
