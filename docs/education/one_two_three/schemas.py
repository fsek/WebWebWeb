from pydantic import BaseModel, ConfigDict


# Inherit from when creating Pydantic Models
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # This model_config lets pydantic validate a databse model


class Book(BaseSchema):
    title: str
    author: str
    ISBN: int
    text: str


class BookBrowse(BaseSchema):
    title: str
    author: str
