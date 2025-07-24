from typing import TYPE_CHECKING
from db_models.base_model import BaseModel_DB
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from db_models.tag_model import Tag_DB

if TYPE_CHECKING:
    from db_models.event_model import Event_DB


class EventTag_DB(BaseModel_DB):
    __tablename__ = "event_tag_table"

    tag_id: Mapped[int] = mapped_column(ForeignKey("tag_table.id"), primary_key=True)
    tag: Mapped["Tag_DB"] = relationship(back_populates="event_tags", init=False)

    event_id: Mapped[int] = mapped_column(ForeignKey("event_table.id"), primary_key=True)
    event: Mapped["Event_DB"] = relationship(back_populates="event_tags", init=False)
