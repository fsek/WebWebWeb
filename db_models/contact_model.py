from helpers.constants import MAX_CONTACT_NAME, MAX_FIRST_NAME_LEN, MAX_LAST_NAME_LEN, MAX_EMAIL
from .base_model import BaseModel_DB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from helpers.types import ContactCategory
from sqlalchemy import Enum


class Contact_DB(BaseModel_DB):
    __tablename__ = "contact_table"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    contact_name: Mapped[str] = mapped_column(String(MAX_CONTACT_NAME), unique=True)

    first_name: Mapped[str] = mapped_column(String(MAX_FIRST_NAME_LEN))
    last_name: Mapped[str] = mapped_column(String(MAX_LAST_NAME_LEN))

    email: Mapped[str] = mapped_column(String(MAX_EMAIL))

    category: Mapped[ContactCategory] = mapped_column(Enum(ContactCategory))
