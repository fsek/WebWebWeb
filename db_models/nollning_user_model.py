from typing import TYPE_CHECKING
from sqlalchemy import Enum, ForeignKey

from db_models.mentor_group_model import MentorGroup_DB
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from user_model import User_DB


class NollningUser_DB(BaseModel_DB):
    __tablename__ = "nollning_user_table"

    user: Mapped["User_DB"] = relationship(back_populates="nollning_users")
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), primary_key=True)

    group: Mapped["MentorGroup_DB"] = relationship(back_populates="group_users")
    group_id: Mapped[int] = mapped_column(ForeignKey("mentor_group_table.id"), primary_key=True)

    nollning_user_type: Mapped[str] = mapped_column(Enum("Mentee", "Mentor", name="nollning_user_enum"))
