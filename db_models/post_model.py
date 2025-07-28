from typing import TYPE_CHECKING, Callable
from sqlalchemy import ForeignKey, String

from db_models.election_post_model import ElectionPost_DB
from helpers.constants import MAX_POST_DESC, MAX_POST_NAME
from .post_door_access_model import PostDoorAccess_DB
from .base_model import BaseModel_DB
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .post_user_model import PostUser_DB
from .post_permission_model import PostPermission_DB

if TYPE_CHECKING:
    from .council_model import Council_DB
    from .post_user_model import PostUser_DB
    from .user_model import User_DB

    from .post_permission_model import PostPermission_DB
    from .permission_model import Permission_DB

creator: Callable[["User_DB"], "PostUser_DB"] = lambda user: PostUser_DB(user=user)
perm_creator: Callable[["Permission_DB"], "PostPermission_DB"] = lambda perm: PostPermission_DB(permission=perm)


class Post_DB(BaseModel_DB):
    __tablename__ = "post_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name_sv: Mapped[str] = mapped_column(String(MAX_POST_NAME))
    name_en: Mapped[str] = mapped_column(String(MAX_POST_NAME))

    council_id: Mapped[int] = mapped_column(ForeignKey("council_table.id"))
    council: Mapped["Council_DB"] = relationship(back_populates="posts", init=False)

    description_sv: Mapped[str] = mapped_column(String(MAX_POST_DESC), nullable=False, default="")
    description_en: Mapped[str] = mapped_column(String(MAX_POST_DESC), nullable=False, default="")

    email: Mapped[str] = mapped_column(nullable=False, default="")

    post_permissions: Mapped[list["PostPermission_DB"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", init=False
    )

    post_door_accesses: Mapped[list["PostDoorAccess_DB"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", init=False
    )

    permissions: AssociationProxy[list["Permission_DB"]] = association_proxy(
        attr="permission", target_collection="post_permissions", creator=perm_creator, init=False
    )

    post_users: Mapped[list["PostUser_DB"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", init=False
    )

    election_posts: Mapped[list["ElectionPost_DB"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", init=False
    )

    users: AssociationProxy[list["User_DB"]] = association_proxy(
        target_collection="post_users", attr="user", creator=creator, init=False
    )
