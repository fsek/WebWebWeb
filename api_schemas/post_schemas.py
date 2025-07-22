from api_schemas.base_schema import BaseSchema


class _PostPermissionRead(BaseSchema):
    id: int
    action: str
    target: str


class PostRead(BaseSchema):
    id: int
    name: str
    council_id: int
    permissions: list[_PostPermissionRead]
    description: str
    email: str

    class Config:
        from_attributes = True


class PostUpdate(BaseSchema):
    name: str | None = None
    council_id: int | None = None
    description: str | None = None
    email: str | None = None


class PostCreate(BaseSchema):
    name: str
    council_id: int
    email: str
    description: str
