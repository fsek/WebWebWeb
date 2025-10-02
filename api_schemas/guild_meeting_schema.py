from api_schemas.base_schema import BaseSchema


class GuildMeetingRead(BaseSchema):
    id: int
    title_sv: str
    title_en: str
    date_description_sv: str
    date_description_en: str
    description_sv: str
    description_en: str
    is_active: bool


class GuildMeetingUpdate(BaseSchema):
    title_sv: str | None = None
    title_en: str | None = None
    date_description_sv: str | None = None
    date_description_en: str | None = None
    description_sv: str | None = None
    description_en: str | None = None
    is_active: bool | None = None
