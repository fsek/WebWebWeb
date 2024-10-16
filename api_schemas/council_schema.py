from typing import Annotated
from pydantic import StringConstraints
from fastapi_users_pelicanq import schemas as fastapi_users_schemas
from api_schemas.base_schema import BaseSchema


class CouncilRead(BaseSchema):
    id: int
    name: str


class CouncilCreate(BaseSchema):
    id: int
    name: str


class CouncilUpdate(BaseSchema):
    name: str | None = None
