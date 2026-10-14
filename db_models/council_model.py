from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, ForeignKey

from db_models.room_booking_model import RoomBooking_DB
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from helpers.constants import MAX_COUNCIL_DESC, MAX_COUNCIL_NAME

if TYPE_CHECKING:
    from .post_model import Post_DB
    from .event_model import Event_DB
    from .car_booking_model import CarBooking_DB


class Council_DB(BaseModel_DB):
    __tablename__ = "council_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name_sv: Mapped[str] = mapped_column(String(MAX_COUNCIL_NAME), unique=True)

    name_en: Mapped[str] = mapped_column(String(MAX_COUNCIL_NAME), unique=True)

    posts: Mapped[list["Post_DB"]] = relationship(
        back_populates="council", foreign_keys="Post_DB.council_id", init=False
    )

    events: Mapped[list["Event_DB"]] = relationship(back_populates="council", cascade="all, delete-orphan", init=False)

    car_bookings: Mapped[list["CarBooking_DB"]] = relationship(
        back_populates="council", cascade="all, delete-orphan", init=False
    )

    room_bookings: Mapped[list["RoomBooking_DB"]] = relationship(
        back_populates="council", cascade="all, delete-orphan", init=False
    )

    description_sv: Mapped[Optional[str]] = mapped_column(String(MAX_COUNCIL_DESC))

    description_en: Mapped[Optional[str]] = mapped_column(String(MAX_COUNCIL_DESC))

    contact_post_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("post_table.id", use_alter=True, ondelete="SET NULL", name="council_contact_post_id_fkey"),
        default=None,
    )

    contact_post: Mapped[Optional["Post_DB"]] = relationship(
        foreign_keys=[contact_post_id], post_update=True, init=False
    )

    pass
