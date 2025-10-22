from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .base_model import BaseModel_DB
from helpers.constants import MAX_GUILD_MEETING_DATE_DESC, MAX_GUILD_MEETING_DESC, MAX_GUILD_MEETING_TITLE
from sqlalchemy import String


class GuildMeeting_DB(BaseModel_DB):
    __tablename__ = "guild_meeting_table"
    __table_args__ = (CheckConstraint("id = 1", name="ck_guild_meeting_singleton"),)

    id: Mapped[int] = mapped_column(primary_key=True, init=False, default=1)
    title_sv: Mapped[str] = mapped_column(String(MAX_GUILD_MEETING_TITLE), default="")
    title_en: Mapped[str] = mapped_column(String(MAX_GUILD_MEETING_TITLE), default="")
    date_description_sv: Mapped[str] = mapped_column(String(MAX_GUILD_MEETING_DATE_DESC), default="")
    date_description_en: Mapped[str] = mapped_column(String(MAX_GUILD_MEETING_DATE_DESC), default="")
    description_sv: Mapped[str] = mapped_column(String(MAX_GUILD_MEETING_DESC), default="")
    description_en: Mapped[str] = mapped_column(String(MAX_GUILD_MEETING_DESC), default="")
    is_active: Mapped[bool] = mapped_column(default=True)
