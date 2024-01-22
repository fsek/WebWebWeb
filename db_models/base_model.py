from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
)
from sqlalchemy.ext.asyncio import AsyncAttrs


class BaseModel_DB(MappedAsDataclass, AsyncAttrs, DeclarativeBase, kw_only=True):
    pass
