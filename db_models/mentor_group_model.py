from sqlalchemy import Enum, String
from typing import TYPE_CHECKING, Optional

from helpers.constants import MAX_GROUP_NAME
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

if TYPE_CHECKING:
    from .user_model import User_DB
    from .nollning_user_model import NollningUser_DB


class MentorGroup_DB(BaseModel_DB):
    __tablename__ = "mentor_group_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column(String(MAX_GROUP_NAME))

    group_type: Mapped[Optional[str]] = mapped_column(
        Enum("mentor_group", "mission_group", name="group_enum"), default=None
    )

    group_users: Mapped[list["NollningUser_DB"]] = relationship(
        back_populates="group", cascade="all, delete-orphan", init=False
    )

    users: AssociationProxy[list["User_DB"]] = association_proxy(
        target_collection="nollning_users", attr="user", init=False
    )
