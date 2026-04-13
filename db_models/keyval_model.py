from db_models.base_model import BaseModel_DB
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from helpers.constants import MAX_KEYVAL_KEY, MAX_KEYVAL_VALUE


class Keyval_DB(BaseModel_DB):
    __tablename__ = "keyval_table"

    key: Mapped[str] = mapped_column(String(MAX_KEYVAL_KEY), primary_key=True)

    value: Mapped[str] = mapped_column(String(MAX_KEYVAL_VALUE), nullable=False)
