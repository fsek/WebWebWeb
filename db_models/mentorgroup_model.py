from sqlalchemy import Enum
from typing import Optional
from .base_model import BaseModel_DB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .user_model import User_DB

class MentorGroup_DB(BaseModel_DB):
    __tablename__ = "mentorgroup_table"
    
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    name: Mapped[str] = mapped_column()

    group_type: Mapped[Optional[str]] = mapped_column(Enum("group_group", "adventure_group", name="group_enum"), default=None)

    mentees: Mapped[list["User_DB"]] = relationship(back_populates="mentee_in_group", init=False)

    #mentors: Mapped