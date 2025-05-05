from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Integer, ForeignKey
from datetime import datetime, timezone
from .base_model import BaseModel_DB
from sqlalchemy import LargeBinary

if TYPE_CHECKING:
    from .council_model import Council_DB


class Document_DB(BaseModel_DB):
    __tablename__ = "document_table"
    path: Mapped[str] = mapped_column(String(511))
    salt: Mapped[int] = mapped_column(Integer)
    document_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    is_private: Mapped[bool] = mapped_column(default=False)
