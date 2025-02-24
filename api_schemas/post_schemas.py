from api_schemas.base_schema import BaseSchema
from api_schemas.user_schemas import UserRead


class _PostPermissionRead(BaseSchema):
    id: int
    action: str
    target: str


class PostRead(BaseSchema):
    id: int
    name: str
    council_id: int
    permissions: list[_PostPermissionRead]


class PostUpdate(BaseSchema):
    name: str
    council_id: int


class PostCreate(BaseSchema):
    name: str
    council_id: int


class PostUserRead(BaseSchema):
    user: UserRead
