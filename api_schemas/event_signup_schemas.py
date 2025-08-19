from api_schemas.base_schema import BaseSchema
from api_schemas.user_schemas import UserInEventRead
from helpers.types import DRINK_PACKAGES


class EventSignupCreate(BaseSchema):
    user_id: int
    priority: str | None = None
    group_name: str | None = None
    drinkPackage: DRINK_PACKAGES | None = "None"


class EventSignupRead(BaseSchema):
    user: UserInEventRead
    event_id: int
    priority: str
    group_name: str | None
    drinkPackage: DRINK_PACKAGES
    confirmed_status: bool


class EventSignupUpdate(BaseSchema):
    user_id: int | None = None
    priority: str | None = None
    group_name: str | None = None
    drinkPackage: DRINK_PACKAGES | None = None


# class EventSignupDelete(BaseSchema):
#     user_id: int
