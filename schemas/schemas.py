from pydantic import BaseModel, ConfigDict
from fastapi_users import schemas as fastapi_users_schemas


# Inherit from when creating Pydantic Models
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # This model_config lets pydantic validate a databse model


class UserCreatedResponse(fastapi_users_schemas.BaseUser[int], BaseSchema):
    # This is a specific response model for 'register' route. fastapi-users lirary uses async SQLAlchemy so
    # this schema can't contain related attributes since they would need lazy load which can't be done with async session
    id: int
    firstname: str
    email: str


class PostRead(BaseSchema):
    id: int
    name: str
    council_id: int


class EventRead(BaseSchema):
    id: int


class UserRead(fastapi_users_schemas.BaseUser[int], BaseSchema):
    firstname: str
    email: str
    posts: list[PostRead]
    events: list[EventRead]


class UserCreate(fastapi_users_schemas.BaseUserCreate, BaseSchema):
    firstname: str
    lastname: str
    pass


class UserUpdate(fastapi_users_schemas.BaseUserUpdate, BaseSchema):
    pass
