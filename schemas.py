from unittest.mock import Base
from pydantic import BaseModel, ConfigDict


# Inherit from when creating Pydantic Models
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # This model_config lets pydantic validate a databse model


class StudentOut(BaseSchema):
    id: int
    year: int


class StudentCreate(BaseSchema):
    card_id: int
    year: int


class TeacherOut(BaseSchema):
    id: int
    name: str


class TeacherCreate(BaseSchema):
    name: str


class BookOut(BaseSchema):
    id: int
    consumed_by_dog: bool


class BookCreate(BaseSchema):
    consumed_by_dog: bool


class BookUpdate(BaseSchema):
    consumed_by_dog: bool
