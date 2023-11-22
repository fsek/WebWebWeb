from pydantic import BaseModel, ConfigDict


# Inherit from when creating Pydantic Models
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # This model_config lets pydantic validate a databse model


# TODO: Add  relevant fields  schemas  once users and books are related


class BookRead(BaseSchema):
    id: int
    title: str


class BookCreate(BaseSchema):
    title: str


class UserCreate(BaseSchema):
    name: str


class UserRead(BaseSchema):
    id: int
    name: str


class AssignPayload(BaseSchema):
    user_id: int
    book_id: int
