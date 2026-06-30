from typing import Optional
from sqlalchemy import CheckConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .base_model import BaseModel_DB

from helpers.constants import MAX_TELEPHONE_LEN


class PreregMember_DB(BaseModel_DB):
    __tablename__ = "prereg_member_table"
    __table_args__ = (
        CheckConstraint(
            "telephone_number IS NOT NULL OR stil_id IS NOT NULL OR email IS NOT NULL",
            name="at_least_one_identifier_required",
        ),
        UniqueConstraint("telephone_number", "stil_id", "email", name="unique_prereg_member_identifiers"),
    )
    prereg_member_id: Mapped[int] = mapped_column(
        primary_key=True, init=False
    )  # Not the id the user will have when confirmed as member!

    telephone_number: Mapped[Optional[str]] = mapped_column(String(MAX_TELEPHONE_LEN), default=None)
    stil_id: Mapped[Optional[str]] = mapped_column(default=None)
    email: Mapped[Optional[str]] = mapped_column(default=None)
