from typing import TYPE_CHECKING, Optional
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey

from helpers.constants import MAX_DOC_FILE_NAME, MAX_DOC_TITLE, MAX_COURSE_DOC_AUTHOR, MAX_COURSE_DOC_SUB_CATEGORY
from .base_model import BaseModel_DB
from helpers.db_util import created_at_column, latest_modified_column
from helpers.types import COURSE_DOCUMENT_CATEGORIES, datetime_utc

if TYPE_CHECKING:
    from .course_model import Course_DB


class CourseDocument_DB(BaseModel_DB):
    __tablename__ = "course_document_table"
    course_document_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title: Mapped[str] = mapped_column(String(MAX_DOC_TITLE), nullable=False)
    file_name: Mapped[str] = mapped_column(String(MAX_DOC_FILE_NAME), nullable=False)

    course_id: Mapped[int] = mapped_column(ForeignKey("course_table.course_id"))

    course: Mapped["Course_DB"] = relationship(back_populates="documents", init=False)

    author: Mapped[str] = mapped_column(String(MAX_COURSE_DOC_AUTHOR), nullable=False)

    category: Mapped[COURSE_DOCUMENT_CATEGORIES] = mapped_column(default="Other")

    # Can be used to separate lecture notes from different authors or years, for example.
    sub_category: Mapped[Optional[str]] = mapped_column(String(MAX_COURSE_DOC_SUB_CATEGORY), default=None)

    created_at: Mapped[datetime_utc] = created_at_column()
    updated_at: Mapped[datetime_utc] = latest_modified_column()
