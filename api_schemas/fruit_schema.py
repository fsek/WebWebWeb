from api_schemas.base_schema import BaseSchema


class FruitRead(BaseSchema):
    id: int
    name: str
    color: str
    price: int
    is_moldy: bool


class FruitCreate(BaseSchema):
    name: str
    color: str
    price: int | None = None


class FruitUpdate(BaseSchema):
    name: str | None = None
    color: str | None = None
    price: int | None = None
