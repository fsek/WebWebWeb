from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String

from db_models.group_model import Group_DB
from helpers.constants import MAX_GROUP_USER_TYPE_NAME
from helpers.types import GROUP_USER_TYPE
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column


if TYPE_CHECKING:
    from user_model import User_DB


class GroupUser_DB(BaseModel_DB):
    __tablename__ = "group_user_table"

    user: Mapped["User_DB"] = relationship(back_populates="group_users")
    user_id: Mapped[int] = mapped_column(ForeignKey("user_table.id"), primary_key=True)

    group: Mapped["Group_DB"] = relationship(back_populates="group_users")
    group_id: Mapped[int] = mapped_column(ForeignKey("group_table.id"), primary_key=True)

    group_user_type: Mapped[GROUP_USER_TYPE] = mapped_column(default="Default")
