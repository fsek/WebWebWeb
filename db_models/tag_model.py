from typing import TYPE_CHECKING, Optional

from sqlalchemy import String

from helpers.constants import MAX_TAG_NAME
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

if TYPE_CHECKING:
    from news_model import News_DB
    from event_model import Event_DB


class Tag_DB(BaseModel_DB):
    __tablename__ = "tag_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    tag_name: Mapped[str] = mapped_column(String(MAX_TAG_NAME))
    color: Mapped[str] = mapped_column(String(7))  # Defined as #ff0000 for example

    events: AssociationProxy[list["Event_DB"]] = association_proxy(
        target_collection="event_tags", attr="tag", init=False
    )

    news: AssociationProxy[list["News_DB"]] = association_proxy(target_collection="news_tags", attr="tag", init=False)
