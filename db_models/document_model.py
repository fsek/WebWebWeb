from typing import TYPE_CHECKING, Optional
from helpers.constants import MAX_DOC_AUTHOR, MAX_DOC_TITLE
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import  ForeignKey, String
from datetime import datetime


if TYPE_CHECKING:
    from .user_model import User_DB


class Document_DB(BaseModel_DB):
    __tablename__ = "document_table"

    document_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title: Mapped[str] = mapped_column(String(MAX_DOC_TITLE))

    date: Mapped[datetime] = mapped_column()

    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user_table.id"), default=None
    )

    user: Mapped[Optional["User_DB"]] = relationship(
        back_populates="documents", init=False
    )
    
    #author: Mapped[Optional[str]] = mapped_column(String(MAX_BOOK_AUTHOR))
    
    #seller: Mapped[User_DB] = relationship(back_populates = "bookads", init = False)
            
    #price: Mapped[Optional[int]] = mapped_column(default = 0)

    #selling: Mapped[bool] = mapped_column(default=True)
    
    #condition: Mapped[int] = mapped_column(default=1) ##1 is best and 3 is worst
    
    pass
