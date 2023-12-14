from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
)


class BaseModel_DB(MappedAsDataclass, DeclarativeBase, kw_only=True):
    pass
