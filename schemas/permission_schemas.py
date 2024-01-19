from typing import Literal
from helpers.types import PERMISSION_TARGET, PERMISSION_TYPE
from schemas.user_schemas import BaseSchema


class PermissionRead(BaseSchema):
    id: int
    action: PERMISSION_TYPE
    target: PERMISSION_TARGET
    # This could fail response validation if a permission is left in db but deleted in hardcoded.
    # alternative is to just say "str" for this schemas action and target


class PermissionCreate(BaseSchema):
    action: PERMISSION_TYPE
    target: PERMISSION_TARGET


class UpdatePermission(BaseSchema):
    post_id: int
    change: Literal["add", "remove"]
    permission_id: int
