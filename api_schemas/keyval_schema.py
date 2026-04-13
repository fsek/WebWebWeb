from typing import Annotated
from pydantic import StringConstraints
from api_schemas.base_schema import BaseSchema
from helpers.constants import MAX_KEYVAL_KEY, MAX_KEYVAL_VALUE


class KeyvalRead(BaseSchema):
    key: str
    value: str


class KeyvalCreate(BaseSchema):
    key: Annotated[str, StringConstraints(max_length=MAX_KEYVAL_KEY)]
    value: Annotated[str, StringConstraints(max_length=MAX_KEYVAL_VALUE)]


class KeyvalUpdate(BaseSchema):
    value: Annotated[str, StringConstraints(max_length=MAX_KEYVAL_VALUE)]
