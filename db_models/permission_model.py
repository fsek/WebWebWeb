from typing import TYPE_CHECKING
from sqlalchemy import String
from helper_types.permission_types import PermissionAction, PermissionTarget
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship

if TYPE_CHECKING:
    from .post_permission_model import PostPermission_DB


class Permission_DB(BaseModel_DB):
    __tablename__ = "permission_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    action: Mapped[PermissionAction] = mapped_column(String(160))

    post_permissions: Mapped[list["PostPermission_DB"]] = relationship(back_populates="permission", init=False)

    target: Mapped[PermissionTarget] = mapped_column(String(160))
