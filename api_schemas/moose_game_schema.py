from api_schemas.base_schema import BaseSchema


class MooseGameRead(BaseSchema):
    moose_game_name: str
    moose_game_score: int
