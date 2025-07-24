from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from .base_model import BaseModel_DB

if TYPE_CHECKING:
    from event_model import Event_DB


class Priority_DB(BaseModel_DB):
    __tablename__ = "priority_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    priority: Mapped[str] = mapped_column()

    event_id: Mapped[int] = mapped_column(ForeignKey("event_table.id"))
    event: Mapped["Event_DB"] = relationship(back_populates="priorities", init=False)
