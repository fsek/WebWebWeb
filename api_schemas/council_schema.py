from api_schemas.base_schema import BaseSchema


class CouncilCreate(BaseSchema):
    name: str


class CouncilRead(BaseSchema):
    name: str
    id: int
