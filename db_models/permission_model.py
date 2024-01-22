from typing import TYPE_CHECKING
from sqlalchemy import String

from helpers.types import PERMISSION_TARGET, PERMISSION_TYPE
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship

if TYPE_CHECKING:
    from .post_permission_model import PostPermission_DB


class Permission_DB(BaseModel_DB):
    __tablename__ = "permission_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    action: Mapped[PERMISSION_TYPE] = mapped_column(String(160))

    post_permissions: Mapped[list["PostPermission_DB"]] = relationship(back_populates="permission", init=False)

    target: Mapped[PERMISSION_TARGET] = mapped_column(String(160))
