from schemas.user_schemas import BaseSchema


class _PostPermissionRead(BaseSchema):
    id: int
    action: str
    target: str


class PostRead(BaseSchema):
    id: int
    name: str
    council_id: int
    permissions: list[_PostPermissionRead]
