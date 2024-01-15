from typing import TYPE_CHECKING, Literal

from sqlalchemy import String
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship


if TYPE_CHECKING:
    from .post_permission_model import PostPermission_DB

a = Literal["read", "write", "destroy"]
b = Literal["A", "B", "C"]


class Permission_DB(BaseModel_DB):
    __tablename__ = "permission_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    action: Mapped[a] = mapped_column(String(160))

    post_permissions: Mapped[list["PostPermission_DB"]] = relationship(back_populates="permission", init=False)

    target: Mapped[b] = mapped_column(String(160))
