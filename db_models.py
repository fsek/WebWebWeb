from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    mapped_column,
    Mapped,
    relationship,
)


class BaseModelDB(DeclarativeBase, MappedAsDataclass):
    pass
