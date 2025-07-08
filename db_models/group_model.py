from sqlalchemy import String
from typing import TYPE_CHECKING


from helpers.constants import MAX_GROUP_NAME, MAX_GROUP_TYPE_NAME
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy


if TYPE_CHECKING:
    from .user_model import User_DB
    from .group_user_model import GroupUser_DB
    from db_models.nollning_model import Nollning_DB
    from db_models.nollning_group_model import NollningGroup_DB


class Group_DB(BaseModel_DB):
    __tablename__ = "group_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column(String(MAX_GROUP_NAME))

    group_type: Mapped[str] = mapped_column(String(MAX_GROUP_TYPE_NAME), default=None)

    group_users: Mapped[list["GroupUser_DB"]] = relationship(
        back_populates="group", cascade="all, delete-orphan", init=False
    )

    users: AssociationProxy[list["User_DB"]] = association_proxy(
        target_collection="group_users", attr="user", init=False
    )

    nollning_groups: Mapped[list["NollningGroup_DB"]] = relationship(
        back_populates="group", cascade="all, delete-orphan", init=False
    )

    nollnings: AssociationProxy[list["Nollning_DB"]] = association_proxy(
        target_collection="nollning_groups", attr="nollning", init=False
    )
