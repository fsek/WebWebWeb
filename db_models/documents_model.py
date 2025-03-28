from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from helpers.constants import MAX_EVENT_DESC, MAX_EVENT_TITLE
from .base_model import BaseModel_DB
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

class Documents_DB(BaseModel_DB):
    __tablename__ = "documents_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[int] = mapped_column(String(MAX_EVENT_TITLE), nullable=False)

    date_uploaded: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    uploader_id: Mapped[int] = mapped_column(ForeignKey("users_table.id"), nullable=False)
    uploader: Mapped["User_DB"] = relationship("User_DB", back_populates="documents", nullable=False)

    file_path: Mapped[str] = mapped_column(String, nullable=False)  # Path or URL to the document file
    file_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # PDF, DOCX, etc.
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)  # Access control
    

    def __repr__(self):
        return f"<Document(id={self.id}, name={self.name}, uploader={self.uploader_id})>"
