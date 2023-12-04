from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    relationship,
    Mapped,
    mapped_column,
)


class BaseModelDB(DeclarativeBase, MappedAsDataclass):
    pass
