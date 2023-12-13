from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, relationship, mapped_column
from db_models.base_model import BaseModel_DB

if TYPE_CHECKING:
    from .event_user_model import EventUser_DB
    from .post_model import Post_DB
    from .post_user_model import PostUser_DB


class User_DB(BaseModel_DB, SQLAlchemyBaseUserTable[int]):
    __tablename__ = "users_table"

    id: Mapped[int] = mapped_column(primary_key=True)  # type: ignore . It's fine

    # posts: Mapped["Post_DB"] = relationship()
    # posts: Mapped["Post_DB"] = relationship()

    # post_user: Mapped["PostUser_DB"] = relationship()
    # event_user: Mapped["EventUser_DB"] = relationship()

    # notifications: Mapped[list["Notification_DB"]]

    # fredmansky: Mapped["Fredmansky_DB"]
