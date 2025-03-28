from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Integer, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship
from helpers.constants import MAX_DOCUMENT_TITLE
from .base_model import BaseModel_DB
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from helpers.types import datetime_utc

if TYPE_CHECKING:
    from .user_model import User_DB


class Documents_DB(BaseModel_DB):
    __tablename__ = "documents_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column(String(MAX_DOCUMENT_TITLE), nullable=False)

    uploader_id: Mapped[int] = mapped_column(ForeignKey("user_table.id", ondelete="SET NULL"), nullable=True)
    user: Mapped["User_DB"] = relationship("User_DB", back_populates="documents", init=False)

    file_path: Mapped[str] = mapped_column(String, nullable=False)  # Path or URL to the document file
    file_type: Mapped[str] = mapped_column(String(50))  # PDF, DOCX, etc.
    date_uploaded: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))

    # def __repr__(self):
    #     return f"<Document(id={self.id}, name={self.name}, uploader={self.uploader_id})>"
