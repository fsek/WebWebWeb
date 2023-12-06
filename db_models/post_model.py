from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from base_model import BaseModel_DB

from sqlalchemy.orm import relationship, Mapped, mapped_column

if TYPE_CHECKING:
    from council_model import Council_DB
    from post_user_model import PostUser_DB


class Post_DB(BaseModel_DB):
    __tablename__ = "posts_table"

    id: Mapped[int] = mapped_column(primary_key=True)

    council: Mapped["Council_DB"] = relationship()
    council_id: Mapped[int] = mapped_column(ForeignKey("councils_table"))

    post_users: Mapped[list["PostUser_DB"]] = relationship()

    # has many users through postusers
