from api_schemas.base_schema import BaseSchema
from pydantic_extra_types.phone_numbers import PhoneNumber


class PreregMemberCreate(BaseSchema):
    telephone_number: PhoneNumber | None = None
    stil_id: str | None = None
    email: str | None = None


class PreregMemberUpdate(BaseSchema):
    telephone_number: PhoneNumber | None = None
    stil_id: str | None = None
    email: str | None = None


class PreregMemberRead(BaseSchema):
    prereg_member_id: int
    telephone_number: PhoneNumber | None = None
    stil_id: str | None = None
    email: str | None = None
