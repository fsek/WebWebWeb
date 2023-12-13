from pydantic import BaseModel, ConfigDict
from fastapi_users import schemas as fastapi_users_schemas


# Inherit from when creating Pydantic Models
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # This model_config lets pydantic validate a databse model


class UserRead(fastapi_users_schemas.BaseUser[int], BaseSchema):
    pass


class UserCreate(fastapi_users_schemas.BaseUserCreate, BaseSchema):
    pass


class UserUpdate(fastapi_users_schemas.BaseUserUpdate, BaseSchema):
    pass
