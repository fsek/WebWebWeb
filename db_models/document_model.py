from typing import TYPE_CHECKING
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey

from helpers.constants import MAX_DOC_CATEGORY, MAX_DOC_FILE_NAME, MAX_DOC_TITLE
from .base_model import BaseModel_DB
from helpers.db_util import created_at_column, latest_modified_column
from helpers.types import datetime_utc

if TYPE_CHECKING:
    from .user_model import User_DB


class Document_DB(BaseModel_DB):
    __tablename__ = "document_table"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title: Mapped[str] = mapped_column(String(MAX_DOC_TITLE), nullable=False)
    file_name: Mapped[str] = mapped_column(String(MAX_DOC_FILE_NAME), nullable=False)
    category: Mapped[str] = mapped_column(String(MAX_DOC_CATEGORY))

    author_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"))
    author: Mapped["User_DB"] = relationship(back_populates="uploaded_documents", init=False)

    created_at: Mapped[datetime_utc] = created_at_column()
    updated_at: Mapped[datetime_utc] = latest_modified_column()

    is_private: Mapped[bool] = mapped_column(default=False)
