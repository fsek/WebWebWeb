from api_schemas.base_schema import BaseSchema


class _PostPermissionRead(BaseSchema):
    id: int
    action: str
    target: str


class PostRead(BaseSchema):
    id: int
    name_sv: str
    name_en: str
    council_id: int
    permissions: list[_PostPermissionRead]
    description_sv: str
    description_en: str
    email: str

    class Config:
        from_attributes = True


class PostUpdate(BaseSchema):
    name_sv: str | None = None
    name_en: str | None = None
    council_id: int | None = None
    description_sv: str | None = None
    description_en: str | None = None
    email: str | None = None


class PostCreate(BaseSchema):
    name_sv: str
    name_en: str
    council_id: int
    email: str
    description_sv: str
    description_en: str
