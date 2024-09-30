from api_schemas.base_schema import BaseSchema


class EventSignupCreate(BaseSchema):
    priority: str | None
    group_name: str | None


class EventSignupUpdate(BaseSchema):
    priority: str | None
    group_name: str | None
