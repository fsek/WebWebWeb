from db_models.election_post_model import ElectionPost_DB
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from helpers.types import datetime_utc
from helpers.db_util import created_at_column

if TYPE_CHECKING:
    from .sub_election_model import SubElection_DB
    from db_models.election_post_model import ElectionPost_DB


class Nomination_DB(BaseModel_DB):
    __tablename__ = "nomination_table"

    nomination_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    sub_election_id: Mapped[int] = mapped_column(ForeignKey("sub_election_table.sub_election_id"))

    sub_election: Mapped["SubElection_DB"] = relationship(back_populates="candidates", init=False)
    sub_election: Mapped["SubElection_DB"] = relationship(back_populates="nominations", init=False)
    nominee_name: Mapped[str] = mapped_column()

    nominee_email: Mapped[str] = mapped_column()

    motivation: Mapped[str] = mapped_column()

    election_post_id: Mapped[int] = mapped_column(ForeignKey("election_post_table.election_post_id"))

    created_at: Mapped[datetime_utc] = created_at_column()

    election_post: AssociationProxy[ElectionPost_DB] = association_proxy(
        target_collection="nominations", attr="election_post", init=False
    )
