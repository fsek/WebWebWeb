from api_schemas.base_schema import BaseSchema
from typing import Annotated
from pydantic import StringConstraints

from helpers.constants import MAX_TOOL_DESC


class ToolCreate(BaseSchema):
    name_sv: str
    name_en: str
    amount: int
    description_sv: Annotated[str, StringConstraints(max_length=MAX_TOOL_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_TOOL_DESC)] | None = None


class ToolRead(BaseSchema):
    id: int
    name_sv: str
    name_en: str
    amount: int
    description_sv: str | None
    description_en: str | None


class ToolUpdate(BaseSchema):
    name_sv: str
    name_en: str
    amount: int
    description_sv: Annotated[str, StringConstraints(max_length=MAX_TOOL_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_TOOL_DESC)] | None = None


class SimpleToolRead(BaseSchema):
    id: int
    amount: int
