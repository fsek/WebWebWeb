from api_schemas.base_schema import BaseSchema

class EventSignupCreate(BaseSchema):
    priority: str | None
    