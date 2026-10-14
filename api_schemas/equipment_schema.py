from api_schemas.base_schema import BaseSchema
from typing import Annotated
from pydantic import StringConstraints

from helpers.constants import MAX_EQUIPMENT_DESC


class EquipmentCreate(BaseSchema):
    name_sv: str
    name_en: str
    amount: int
    description_sv: Annotated[str, StringConstraints(max_length=MAX_EQUIPMENT_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_EQUIPMENT_DESC)] | None = None


class EquipmentRead(BaseSchema):
    id: int
    name_sv: str
    name_en: str
    amount: int
    description_sv: str | None
    description_en: str | None


class EquipmentUpdate(BaseSchema):
    name_sv: str
    name_en: str
    amount: int
    description_sv: Annotated[str, StringConstraints(max_length=MAX_EQUIPMENT_DESC)] | None = None
    description_en: Annotated[str, StringConstraints(max_length=MAX_EQUIPMENT_DESC)] | None = None


class SimpleEquipmentRead(BaseSchema):
    id: int
    amount: int
