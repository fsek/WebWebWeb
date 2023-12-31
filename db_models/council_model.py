from typing import TYPE_CHECKING
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship


if TYPE_CHECKING:
    from post_model import Post_DB


class Council_DB(BaseModel_DB):
    __tablename__ = "councils_table"

    id: Mapped[int] = mapped_column(primary_key=True)

    posts: Mapped[list["Post_DB"]] = relationship()

    # has many users through posts

    pass
