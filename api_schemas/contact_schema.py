from api_schemas.base_schema import BaseSchema
from helpers.types import ContactCategory


class ContactCreate(BaseSchema):
    contact_name: str
    first_name: str
    last_name: str
    email: str
    category: ContactCategory


class ContactRead(BaseSchema):
    id: int
    contact_name: str
    first_name: str
    last_name: str
    email: str
    category: ContactCategory


class ContactUpdate(BaseSchema):
    contact_name: str
    first_name: str
    last_name: str
    email: str
    category: ContactCategory


class SimpleContactRead(BaseSchema):
    id: int
    contact_name: str
    email: str
