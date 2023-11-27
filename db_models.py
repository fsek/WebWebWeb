from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
)


class BaseModelDB(DeclarativeBase, MappedAsDataclass):
    pass
