from db_models.nomination_post_model import Nomination_DB
from db_models.election_post_model import ElectionPost_DB
from .base_model import BaseModel_DB
from helpers.constants import MAX_NOMINATION_NAME, MAX_NOMINATION_MOTIVATION, MAX_NOMINATION_MAIL
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy


if TYPE_CHECKING:
    from .election_model import Election_DB
    from db_models.nomination_post_model import Nomination_DB
    from db_models.election_post_model import ElectionPost_DB


class Nominee_DB(BaseModel_DB):
    __tablename__ = "nominee_table"

    nominee_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    election_id: Mapped[int] = mapped_column(ForeignKey("election_table.election_id"))

    election: Mapped["Election_DB"] = relationship("Election_DB", back_populates="nominations", init=False)

    name: Mapped[str] = mapped_column(String(MAX_NOMINATION_NAME))
    mail: Mapped[str] = mapped_column(String(MAX_NOMINATION_MAIL))
    motivation: Mapped[str] = mapped_column(String(MAX_NOMINATION_MOTIVATION))

    nominations: Mapped[list["Nomination_DB"]] = relationship(
        back_populates="nominee", cascade="all, delete-orphan", init=False
    )

    election_post: AssociationProxy[list["ElectionPost_DB"]] = association_proxy(
        target_collection="nominations", attr="election_post", init=False
    )
