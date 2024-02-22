import datetime
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
)


# Base DB model. Inherit from this one when you create your own DB models.
# MappedAsDataclass is what automatically creates the model's constructor, __init__(),
# with proper function arguments
class BaseModel_DB(DeclarativeBase, MappedAsDataclass, kw_only=True):
    type_annotation_map = {
        datetime.datetime: TIMESTAMP(timezone=True),
        # Without this, Mapped[datetime] will map to Postgres timestamp without timezone
    }
    pass
