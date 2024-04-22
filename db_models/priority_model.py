
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from helpers.types import MEMBER_TYPE
from .base_model import BaseModel_DB


class Priority_DB(BaseModel_DB):
    __tablename__ = "priority_table"
    
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    
    priority: Mapped[str] = mapped_column(Enum=MEMBER_TYPE)
    
    event_id: Mapped[int] = mapped_column(ForeignKey("event_table.id"))
