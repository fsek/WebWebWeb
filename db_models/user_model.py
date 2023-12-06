from typing import TYPE_CHECKING, Any
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.orm import Mapped, relationship
from database import get_async_session
from db_models.base_model import BaseModel_DB
from sqlalchemy.ext.asyncio import AsyncSession


if TYPE_CHECKING:
    from .event_user_model import EventUser_DB
    from .post_model import Post_DB
    from .post_user_model import PostUser_DB


class User_DB(SQLAlchemyBaseUserTableUUID, BaseModel_DB):
    __tablename__ = "users_table"

    posts: Mapped["Post_DB"] = relationship()
    posts: Mapped["Post_DB"] = relationship()

    post_user: Mapped["PostUser_DB"] = relationship()
    event_user: Mapped["EventUser_DB"] = relationship()

    # notifications: Mapped[list["Notification_DB"]]

    # fredmansky: Mapped["Fredmansky_DB"]


async def get_user_db(session: AsyncSession = Depends(get_async_session)) -> Any:
    yield SQLAlchemyUserDatabase(session, User_DB)
