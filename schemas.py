from pydantic import BaseModel, ConfigDict


# Inherit from when creating Pydantic Models
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # This model_config lets pydantic validate a databse model


class BookRead(BaseSchema):
    id: int
    title: str
    user_id: int | None


class BookCreate(BaseSchema):
    title: str


class UserCreate(BaseSchema):
    name: str
    age: int
    password: str


class UserRead(BaseSchema):
    id: int
    name: str
    age: int
    books: list[BookRead]
