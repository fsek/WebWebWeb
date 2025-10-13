from api_schemas.base_schema import BaseSchema


class ToolCreate(BaseSchema):
    name_sv: str
    name_en: str
    description_sv: str | None = None
    description_en: str | None = None


class ToolRead(BaseSchema):
    id: int
    name_sv: str
    name_en: str
    description_sv: str | None
    description_en: str | None


class ToolUpdate(BaseSchema):
    name_sv: str | None = None
    name_en: str | None = None
    description_sv: str | None = None
    description_en: str | None = None
