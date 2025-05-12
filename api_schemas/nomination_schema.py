from api_schemas.base_schema import BaseSchema


class NominationRead(BaseSchema):
    nominee_id: int
    election_id: int
    mail: str
    name: str
    motivation: str


class NominationCreate(BaseSchema):
    mail: str
    name: str
    motivation: str
