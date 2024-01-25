from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
)


# Base DB model. Inherit from this one when you create your own DB models.
# MappedAsDataclass is what automatically creates the model's constructor, __init__(),
# with proper function arguments
class BaseModel_DB(MappedAsDataclass, DeclarativeBase, kw_only=True):
    pass
