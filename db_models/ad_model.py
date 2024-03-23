from typing import Optional
from db_models.user_model import User_DB
from helpers.constants import MAX_BOOK_AUTHOR, MAX_BOOK_CONTENT, MAX_BOOK_TITLE
from .base_model import BaseModel_DB
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import  String


class BookAd_DB(BaseModel_DB):
    __tablename__ = "bookad_table"

    ad_id: Mapped[int] = mapped_column(primary_key=True, init=False)

    title: Mapped[str] = mapped_column(String(MAX_BOOK_TITLE))
        
    course: Mapped[Optional[str]] = mapped_column(String(MAX_BOOK_TITLE))
    
    author: Mapped[Optional[str]] = mapped_column(String(MAX_BOOK_AUTHOR))
        
    seller: Mapped[str] = mapped_column(String(MAX_BOOK_AUTHOR))
    
    price: Mapped[Optional[int]] = mapped_column(default = 0)

    selling: Mapped[bool] = mapped_column(default=True)
    
    condition: Mapped[int] = mapped_column(default=1) ##1 is best and 3 is worst
    
    pass
